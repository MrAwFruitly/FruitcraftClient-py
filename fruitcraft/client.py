from typing import Optional
import string
import random
import time
import httpx
import asyncio
import pydantic
from .f_types import (
    DScaffold,
    APIResponse,
    Achievements,
    AttackCardInfo,
    BattleRequest,
    BattleResponse,
    Bundles,
    CardsSelection,
    CardInfo,
    Coaching,
    CoolOffRequest,
    CoolOffResponse,
    DailyReward,
    DeviceConstants,
    DeviceConstantsRequest,
    ErrorMessages,
    ErrorMessagesRequest,
    FillPotionRequest,
    FillPotionResponse,
    FruitCardInfo,
    FruitExportContainer,
    FruitJsonExportRequest,
    GetOpponentsRequest,
    GetOpponentsResponse,
    GetPlayerInfoRequest,
    GetPlayerInfoResponse,
    GlobalRankingsRequest,
    GlobalRankingsResponse,
    GoldPackInfo,
    HeroIDSet,
    HeroItems,
    IntArray,
    HeroItemInfo,
    LanguagePatchRequest,
    LanguagePathResponse,
    LeagueRankingsRequest,
    LeagueRankingsResponse,
    LeagueWinnerRanges,
    LiveBattleHelpRequest,
    LiveBattleRequest,
    LiveBattleResponse,
    ModulesVersion,
    new_int_array,
    Onsale,
    OpponentInfo,
    PlayerLeagueRankingInfo,
    PlayerComebackRequest,
    PlayerLoadRequest,
    PlayerLoadResponse,
    PlayerMedals,
    PlayerRankingInfo,
    PotionizeRequest,
    PotionizeResponse,
    Price,
    QuestRequest,
    QuestResponse,
    Scaffold,
    SetCardForLiveBattleRequest,
    SetCardForLiveBattleResponse,
    Tribe,
    TribeInfo,
    TribeMemberInfo,
    TribeMembersRequest,
    TribeMembersResponse,
    TribeRankingsRequest,
    TribeRankingsResponse,
)
from .f_types.utils import (
    xor_decrypt,
    choose_strongest_atk_ids,
    choose_strongest_atk_id,
    hash_q_string,
)
from .f_types.errors import (
    UnknownError,
    PlayerLoadException,
)
import inspect
import json
import logging

_MAX_PASSPORT_LENGTH = 32

class FruitCraftClient():
    passport: str = ""
    http_client: httpx.AsyncClient = None
    cool_off_sleep_time: Optional[int] = None
    attacks_today: int = 0
    
    last_loaded_player: PlayerLoadResponse = None
    last_battle_request: BattleRequest = None
    login_options: PlayerLoadRequest = None
    
    log_player_id_before_atk: bool = False
    log_before_resp_parsing: bool = False
    log_before_req_sending: bool = False
    last_q_value: str = ""
    logger: logging.Logger = None
    mut: asyncio.Lock = None
    _default_url = "\u0068\u0074\u0074\u0070\u003a\u002f\u002f\u0069\u0072\u0061\u006e\u002e\u0066\u0072\u0075\u0069\u0074\u0063\u0072\u0061\u0066\u0074\u002e\u0069\u0072"
    _serialize_key: str = None
    _error_codes_to_sleep = { # times are in seconds
        156: 4,
        124: 2,
        184: 2,
    }
    _max_login_tries: int = 50

    def __init__(self, passport: str = None):
        if not passport:
            passport = FruitCraftClient.generate_passport()
        
        self.mut = asyncio.Lock()
        self.http_client = httpx.AsyncClient()
        self.passport = passport
        if not self.logger:
            self.logger = logging.getLogger(__name__)
    
    async def get_error_messages(self) -> ErrorMessages:
        return await self.get_device_constants_with_options(ErrorMessagesRequest())
    
    async def get_error_messages_with_options(self, opt: ErrorMessagesRequest) -> ErrorMessages:
        opt.set_default_values()
        
        api_response: APIResponse = await self.send_and_parse("device/constants", opt, ErrorMessages)
        return api_response.data
    
    async def get_device_constants(self) -> DeviceConstants:
        return await self.get_device_constants_with_options(DeviceConstantsRequest())
    
    async def get_device_constants_with_options(self, opt: DeviceConstantsRequest) -> DeviceConstants:
        opt.set_default_values()
        api_response: APIResponse = await self.send_and_parse("device/constants", opt, DeviceConstants)
        return api_response.data
    
    async def do_quest(self, cards: CardsSelection) -> QuestResponse:
        return await self.do_quest_with_options(
            QuestRequest(
                cards=new_int_array(cards.cards),
                _cards_selection=cards,
                hero_id=cards.hero_id,
            )
        )
    
    async def do_quest_with_options(self, opt: QuestRequest) -> QuestResponse:
        await self.mut.acquire()
        
        try:
            self.login_options = opt
            resp = await self.__do_quest_with_options(opt)
            self.mut.release()
            return resp
        except Exception as e:
            # just don't forget to release the lock in case an exception occurs
            # because it's going to become a headache later on.
            self.mut.release()
            raise e
    
    async def __do_quest_with_options(self, opt: QuestRequest) -> QuestResponse:
        if self.last_q_value:
            opt.check = hash_q_string(self.last_q_value)
        
        api_response: APIResponse = await self.send_and_parse("battle/quest", opt, QuestResponse)
        if isinstance(api_response.data, QuestResponse):
            if api_response.data.q:
                self.last_q_value = str(api_response.data.q)
            
            return api_response.data
    
    def get_strongest_cards(self) -> CardsSelection:
        if not self.last_loaded_player:
            raise Exception("No player loaded")
        
        cards = choose_strongest_atk_ids(4, *self.last_loaded_player.cards)
        
        if self.last_loaded_player.hero_id_set:
            hero_id = choose_strongest_atk_id(*self.last_loaded_player.hero_id_set)
            if hero_id:
                cards.append(hero_id)
        
        return CardsSelection(
            cards=cards,
            hero_id=hero_id,
        )
    
    
    def get_level1_card(self) -> CardsSelection:
        final_cards: AttackCardInfo = None
        final_since: int = 0
        
        for current in self.last_loaded_player.cards:
            if current.power > 40:
                continue
            
            my_since = time.time() - current.internal_last_time_used
            if my_since < 16:
                continue
            
            if not final_cards:
                final_cards = current
                continue
            
            if my_since > final_since:
                final_cards = current
                final_since = my_since
        
        if not final_cards:
            return None
        
        return CardsSelection(
            cards=[final_cards.id],
            no_heal=True,
        )
        
    
    def get_weakest_card(self) -> CardsSelection:
        if not self.last_loaded_player:
            raise Exception("No player loaded")
        
        level1_selection = self.get_level1_card()
        if level1_selection:
            return level1_selection
        
        target_card = self.last_loaded_player.cards[0]
        for current_card in self.last_loaded_player.cards:
            if current_card.power < target_card.power:
                target_card = current_card
                
        return CardsSelection(
            cards=[target_card.id],
        )
    
    async def load_player(
        self, 
        restore_key: str, 
        game_version: str = "", 
        uid: str = "",
        os_type: int = 0,
        os_version: str = "",
        phone_model: str = "",
        metrix_uid: str = "",
        apps_flyer_uid: str = "",
        device_name: str = "",
        store_type: str = "",
    ) -> PlayerLoadResponse:
        return await self.load_player_with_options(
            PlayerLoadRequest(
                game_version=game_version,
                udid=uid,
                os_type=os_type,
                restore_key=restore_key,
                os_version=os_version,
                model=phone_model,
                metrix_uid=metrix_uid,
                appsflyer_uid=apps_flyer_uid,
                device_name=device_name,
                store_type=store_type,
            )
        )
    
    async def load_player_with_options(self, opt: PlayerLoadRequest) -> PlayerLoadResponse:
        await self.mut.acquire()
        opt.set_default_values()
        
        try:
            self.login_options = opt
            resp = await self.__load_player_with_options(opt)
            self.mut.release()
            return resp
        except Exception as e:
            # just don't forget to release the lock in case an exception occurs
            # because it's going to become a headache later on.
            self.mut.release()
            raise e
    
    """
        Unsafe way of loading the player, please use the `load_player_with_options` method instead.
    """
    async def __load_player_with_options(self, opt: PlayerLoadRequest) -> PlayerLoadResponse:
        current_tries = 0
        while True:
            api_response: APIResponse = await self.send_and_parse("player/load", opt, PlayerLoadResponse)
            if api_response.data != None and self.is_sim_err_code(getattr(api_response.data, "code", None)):
                if current_tries > self._max_login_tries:
                    raise PlayerLoadException("Max login tries reached", api_response.data)
                
                sleep_amount: int = self._error_codes_to_sleep[getattr(api_response.data, "code")]
                self.logger.warning("player/load: sleeping for %s seconds", sleep_amount)
                await asyncio.sleep(sleep_amount)
                current_tries += 1
                continue
            
            break
        
        load_response = api_response.data
        if not isinstance(load_response, PlayerLoadResponse):
            raise PlayerLoadException("Unknown error occurred", api_response.data)
        
        self.login_options = opt
        self.last_q_value = str(load_response.q)
        self.last_loaded_player = load_response
        return load_response
            
        
    def is_sim_err_code(self, value: int) -> bool:
        if not value or not isinstance(value, int):
            return False

        return value in self._error_codes_to_sleep
    
    def set_login_options_str(self, value: str) -> PlayerLoadRequest:
        j_value = json.loads(value)
        
        load_req: PlayerLoadRequest = PlayerLoadRequest(**j_value)
        self.set_login_options(load_req)
        return load_req
    
    def set_login_options(self, login_options: PlayerLoadRequest) -> None:
        self.login_options = login_options
    
    def set_as_load_response(self, value: str) -> PlayerLoadResponse:
        j_value = json.loads(value)
        if not j_value or not j_value['status']:
            raise UnknownError(f"Unknown error occurred", value)
        
        loaded_response: PlayerLoadResponse = PlayerLoadResponse(**j_value['data'])
        self.set_as_player_loaded_value(loaded_response)
        return loaded_response
    
    def set_as_player_loaded_value(self, loaded_value: PlayerLoadResponse):
        self.last_loaded_player = loaded_value

    async def send_and_parse(self, req_path: str, req_data: DScaffold, return_type: type = None) -> APIResponse:
        serialized_data = req_data.get_serialized(self._serialize_key)
        
        parser_method = getattr(req_data, 'parse_response', None)
        if not return_type and not parser_method:
            return None

        respond_bytes = await self.invoke_request(path=req_path, data=serialized_data, the_pass=self.passport)
        if parser_method and inspect.ismethod(parser_method):
            return parser_method(respond_bytes)
        
        if self.log_before_resp_parsing:
            print(f"Response: {respond_bytes}")
        
        respond_decrypted = xor_decrypt(respond_bytes)
        j_value = json.loads(respond_decrypted)
        if not j_value or not j_value['status']:
            raise UnknownError(f"Unknown error occurred for {req_path}", respond_bytes)
        
        api_response: APIResponse = APIResponse(j_value)
        response_data = j_value['data']
        if return_type:
            api_response.data = return_type(**response_data)
        
        return api_response
        

    async def invoke_request(self, path: str, data: str, the_pass: str) -> bytes:
        data_value = f'edata={data}'.encode('utf-8')
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Content-Length': str(len(data_value)),
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; google Pixel 2 Build/LMY47I)',
            'Host': 'iran.fruitcraft.ir'
        }

        if the_pass == "":
            the_pass = self.passport

        if the_pass != "" and the_pass != "none" and the_pass != "null":
            headers['Cookie'] = f"\u0046\u0052\u0055\u0049\u0054\u0050\u0041\u0053\u0053\u0050\u004f\u0052\u0054={the_pass};"

        response = await self.http_client.post(f"{self._default_url}/{path}", data=data_value, headers=headers)
        response.raise_for_status()
        return response.content
        

    
    @staticmethod
    def generate_passport() -> str:
        return ''.join(random.choices("abcdef0123456789", k=_MAX_PASSPORT_LENGTH))
    

