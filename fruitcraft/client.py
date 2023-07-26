from typing import (
    Optional, List, Union
)
import string
import random
import time
import httpx
import asyncio
from .f_types import (
    DScaffold,
    APIResponse,
    AttackCardInfo,
    BattleRequest,
    BattleResponse,
    CardsSelection,
    CardInfo,
    CoolOffRequest,
    CoolOffResponse,
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
    LanguagePatchRequest,
    LanguagePathResponse,
    LeagueRankingsRequest,
    LeagueRankingsResponse,
    LeagueWinnerRanges,
    LiveBattleHelpRequest,
    LiveBattleHelpResponse,
    LiveBattleRequest,
    LiveBattleResponse,
    new_int_array,
    PlayerComebackRequest,
    PlayerComebackResponse,
    PlayerLoadRequest,
    PlayerLoadResponse,
    PotionizeRequest,
    PotionizeResponse,
    QuestRequest,
    QuestResponse,
    SetCardForLiveBattleRequest,
    SetCardForLiveBattleResponse,
    TribeMembersRequest,
    TribeMembersResponse,
    TribeRankingsRequest,
    TribeRankingsResponse,
    CollectGoldRequest,
    CollectGoldResponse,
    EvolveCardRequest,
    EvolveCardResponse,
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
    FruitServerException,
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
    cached_errors: ErrorMessages = None
    
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
    
    async def evolve_card(self, sacrifices: Union[CardsSelection, int]) -> EvolveCardResponse:
        if isinstance(sacrifices, int):
            sacrifices = new_int_array([sacrifices])
        
        return await self.evolve_card_with_options(EvolveCardRequest(
            sacrifices=sacrifices,
        ))
    
    async def evolve_card_with_options(self, opt: EvolveCardRequest) -> EvolveCardResponse:
        api_response: APIResponse = await self.send_and_parse(
            "cards/evolve", opt, EvolveCardResponse)
        return api_response.data
    
    async def collect_gold(self) -> CollectGoldResponse:
        return await self.collect_gold_with_options(CollectGoldRequest())
    
    async def collect_gold_with_options(self, opt: CollectGoldRequest) -> CollectGoldResponse:
        opt.set_default_values()
        
        api_response: APIResponse = await self.send_and_parse(
            "cards/collectgold", opt, CollectGoldResponse)
        return api_response.data
    
    async def get_player_info(self, player_id: int) -> GetPlayerInfoResponse:
        return await self.get_player_info_with_options(GetPlayerInfoRequest(player_id=player_id))
    
    async def get_player_info_with_options(self, opt: GetPlayerInfoRequest) -> GetPlayerInfoResponse:
        api_response: APIResponse = await self.send_and_parse(
            "player/getplayerinfo", opt, GetPlayerInfoResponse)
        return api_response.data
    
    async def potionize(self, hero_id: int, amount: int) -> PotionizeResponse:
        return await self.potionize_with_options(PotionizeRequest(potion=amount, hero_id=hero_id))
    
    async def potionize_with_options(self, opt: PotionizeRequest) -> PotionizeResponse:
        api_response: APIResponse = await self.send_and_parse(
            "cards/potionize", opt, PotionizeResponse)
        
        player_potion = getattr(api_response.data, "player_potion", None)
        if player_potion != None and isinstance(player_potion, int):
            self.last_loaded_player.potion_number = player_potion
        
        return api_response.data
    
    async def fill_potions(self, amount: int = None) -> FillPotionResponse:
        return await self.fill_potions_with_options(FillPotionRequest(amount=amount))
    
    async def fill_potions_with_options(self, opt: FillPotionRequest) -> FillPotionResponse:
        if not opt.amount and self.last_loaded_player:
            opt.amount = 50 - self.last_loaded_player.potion_number
            
            if not opt.amount:
                return FillPotionResponse(potion_number=self.last_loaded_player.potion_number)
        
        api_response: APIResponse = await self.send_and_parse(
            "player/fillpotion", opt, FillPotionResponse)
        
        fill_result = api_response.data
        if not isinstance(fill_result, FillPotionResponse):
            return None
        
        if self.last_loaded_player:
            self.last_loaded_player.potion_number = fill_result.potion_number
        
        return api_response.data
    
    async def get_league_rankings(self) -> LeagueRankingsResponse:
        return await self.get_league_rankings_with_options(LeagueRankingsRequest())
    
    async def get_league_rankings_with_options(self, opt: LeagueRankingsRequest) -> LeagueRankingsResponse:
        opt.set_default_values()
        
        api_response: APIResponse = await self.send_and_parse(
            "ranking/league", opt, LeagueRankingsResponse)
        return api_response.data
    
    async def get_global_rankings(self) -> GlobalRankingsResponse:
        return await self.get_global_rankings_with_options(GlobalRankingsRequest())
    
    async def get_global_rankings_with_options(self, opt: GlobalRankingsRequest) -> GlobalRankingsResponse:
        opt.set_default_values()
        
        api_response: APIResponse = await self.send_and_parse(
            "ranking/global", opt, GlobalRankingsResponse)
        return api_response.data
    
    async def get_tribe_rankings(self) -> TribeRankingsResponse:
        return await self.get_tribe_rankings_with_options(TribeRankingsRequest())
    
    async def get_tribe_rankings_with_options(self, opt: TribeRankingsRequest) -> TribeRankingsResponse:
        opt.set_default_values()
        
        api_response: APIResponse = await self.send_and_parse(
            "ranking/tribe", opt, TribeRankingsResponse)
        return api_response.data
    
    async def live_battle_help(self, battle_id: int) -> bool:
        return await self.live_battle_help_with_options(LiveBattleHelpRequest(
            battle_id=battle_id,
        ))
    
    async def live_battle_help_with_options(self, opt: LiveBattleHelpRequest) -> bool:
        api_response: APIResponse = await self.send_and_parse(
            "live-battle/help", opt, LiveBattleHelpResponse)
        return api_response.status
    
    async def set_card_for_live_battle(self, opt: SetCardForLiveBattleRequest) -> SetCardForLiveBattleResponse:
        api_response: APIResponse = await self.send_and_parse(
            "live-battle/setcardforlivebattle", opt, SetCardForLiveBattleResponse)
        return api_response.data
    
    async def do_live_battle(self, opponent_id: int) -> LiveBattleResponse:
        return await self.do_live_battle_with_options(LiveBattleRequest(
            opponent_id=opponent_id,
        ))
    
    async def do_live_battle_with_options(self, opt: LiveBattleRequest) -> LiveBattleResponse:
        if not isinstance(opt.opponent_id, int) and opt.opponent_id != None:
            tmp_id = getattr(opt.opponent_id, "id", None)
            if isinstance(tmp_id, int):
                opt.opponent_id = tmp_id
        
        api_response: APIResponse = await self.send_and_parse(
            "live-battle/livebattle", opt, LiveBattleResponse)
        return api_response.data
    
    def set_cool_off_sleep_amount(self, sleep_amount: int) -> None:
        self.cool_off_sleep_time = sleep_amount
    
    async def heal_all(self, cards: CardsSelection) -> List[CoolOffResponse]:
        return await self.heal_all_with_ids(*cards.cards)
    
    async def heal_all_with_ids(self, *card_ids) -> List[CoolOffResponse]:
        results = []
        for current_id in card_ids:
            try:
                results.append(await self.cool_off(current_id))
            except Exception as ex:
                self.logger.warning(f"failed to heal card {current_id}: {ex}")
            
            if self.cool_off_sleep_time:
                await asyncio.sleep(self.cool_off_sleep_time)
        
        return results
    
    async def cool_off(self, card_id: int) -> CoolOffResponse:
        return await self.cool_off_with_options(
            CoolOffRequest(
                card_id=card_id,
            )
        )
    
    async def cool_off_with_options(self, opt: CoolOffRequest) -> CoolOffResponse:
        api_response: APIResponse = await self.send_and_parse("cards/cooloff", opt, CoolOffResponse)
        return api_response.data
    
    async def do_battle_and_heal(self, opponent_id: int, cards: CardsSelection) -> BattleResponse:
        battle_result = await self.do_battle(opponent_id=opponent_id, cards=cards)
        await self.heal_all(cards=cards)
        return battle_result
    
    async def do_battle(self, opponent_id: int, cards: CardsSelection) -> BattleResponse:
        return await self.do_battle_with_options(
            BattleRequest(
                cards=new_int_array(cards.cards),
                _cards_selection=cards,
                hero_id=cards.hero_id,
                opponent_id=opponent_id,
            )
        )
    
    async def do_battle_with_options(self, opt: BattleRequest) -> BattleResponse:
        await self.mut.acquire()
        
        try:
            resp = await self.__do_battle_with_options(opt)
            self.mut.release()
            return resp
        except Exception as e:
            # just don't forget to release the lock in case an exception occurs
            # because it's going to become a headache later on.
            self.mut.release()
            raise e
    
    async def __do_battle_with_options(self, opt: BattleRequest) -> BattleResponse:
        if self.last_q_value:
            opt.check = hash_q_string(self.last_q_value)
        
        opt._cards_selection
        
        api_response: APIResponse = await self.send_and_parse("battle/battle", opt, BattleResponse)
        if isinstance(api_response.data, BattleResponse):
            if api_response.data.q:
                self.last_q_value = str(api_response.data.q)
            
            return api_response.data
    
    async def get_opponents_from_others(self, other_pass: str) -> GetOpponentsResponse:
        return await self.get_opponents_with_options(GetOpponentsRequest(_other_pass=other_pass))
    
    async def get_opponents(self) -> GetOpponentsResponse:
        return await self.get_opponents_with_options(GetOpponentsRequest())
    
    async def get_opponents_with_options(self, opt: GetOpponentsRequest) -> GetOpponentsResponse:
        api_response: APIResponse = await self.send_and_parse("battle/getopponents", opt, GetOpponentsResponse)
        return api_response.data
    
    async def get_tribe_members(self) -> TribeMembersResponse:
        return await self.get_tribe_members_with_options(TribeMembersRequest())
    
    async def get_tribe_members_with_options(self, opt: TribeMembersRequest) -> TribeMembersResponse:
        api_response: APIResponse = await self.send_and_parse("tribe/members", opt, TribeMembersResponse)
        return api_response.data
    
    async def player_comeback(self) -> bool:
        return await self.player_comeback_with_options(PlayerComebackRequest())
    
    async def player_comeback_with_options(self, opt: PlayerComebackRequest) -> bool:
        opt.set_default_values()
        
        api_response: APIResponse = await self.send_and_parse("player/comeback", opt, PlayerComebackResponse)
        return api_response.status
    
    async def fruits_json_export(self) -> LanguagePathResponse:
        return await self.fruits_json_export_with_options(FruitJsonExportRequest())
    
    async def fruits_json_export_with_options(self, opt: FruitJsonExportRequest) -> FruitExportContainer:
        opt.set_default_values()
        
        api_response: APIResponse = await self.send_and_parse("cards/fruitsjsonexport", opt, FruitExportContainer)
        return api_response.data
    
    async def get_language_patch(self) -> LanguagePathResponse:
        return await self.get_language_patch_with_options(LanguagePatchRequest())
    
    async def get_language_patch_with_options(self, opt: LanguagePatchRequest) -> LanguagePathResponse:
        opt.set_default_values()
        
        api_response: APIResponse = await self.send_and_parse("player/languagepatch", opt, LanguagePathResponse)
        return api_response.data
    
    async def get_error_messages(self) -> ErrorMessages:
        return await self.get_error_messages_with_options(ErrorMessagesRequest())
    
    async def get_error_messages_with_options(self, opt: ErrorMessagesRequest) -> ErrorMessages:
        opt.set_default_values()
        
        api_response: APIResponse = await self.send_and_parse("error/messages", opt, ErrorMessages)
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
    
    async def do_quest_with_options_str(self, value: str) -> QuestResponse:
        j_value = json.loads(value)
        the_req = QuestRequest(**j_value)
        return await self.do_quest_with_options(the_req)
    
    async def do_quest_with_hash(self, the_hash: str, *cards) -> QuestResponse:
        return await self.do_quest_with_options(
            QuestRequest(
                cards=new_int_array(list(cards)),
                check=the_hash,
            )
        )
    
    async def do_quest_with_options(self, opt: QuestRequest) -> QuestResponse:
        await self.mut.acquire()
        
        try:
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
        
        opt._cards_selection
        
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
        final_card: AttackCardInfo = None
        final_since: int = 0
        
        for current in self.last_loaded_player.cards:
            if current.power > 40:
                continue
            
            my_since = time.time() - current.internal_last_time_used
            if my_since < 16:
                continue
            
            if not final_card:
                final_card = current
                continue
            
            if my_since > final_since:
                final_card = current
                final_since = my_since
        
        if not final_card:
            return None
        
        final_card.set_as_used()
        return CardsSelection(
            cards=[final_card.id],
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
            api_response: APIResponse = await self.send_and_parse(
                "player/load", opt, PlayerLoadResponse, no_err_handling=True)
            if api_response.data != None and self.is_sim_err_code(getattr(api_response.data, "code", None)):
                if current_tries > self._max_login_tries:
                    raise PlayerLoadException("Max login tries reached", api_response.data)
                
                sleep_amount: int = self._error_codes_to_sleep[getattr(api_response.data, "code")]
                self.logger.warning("player/load: sleeping for %i seconds", sleep_amount)
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

    async def get_error_by_code(self, req_path: str, error_code: int, response: str = None) -> Exception:
        if not self.cached_errors:
            self.cached_errors = await self.get_error_messages()
        
        return FruitServerException(
            req_path=req_path, 
            error_code=error_code,
            message=self.cached_errors[str(error_code)],
            response=response
        )

    async def send_and_parse(
        self,
        req_path: str,
        req_data: DScaffold,
        return_type: type = None,
        no_err_handling: bool = False
    ) -> APIResponse:
        serialized_data = req_data.get_serialized(self._serialize_key)
        
        parser_method = getattr(req_data, 'parse_response', None)
        if not return_type and not parser_method:
            return None

        target_pass = getattr(req_data, "_other_pass", None)
        if not target_pass:
            target_pass = self.passport

        respond_bytes = await self.invoke_request(path=req_path, data=serialized_data, the_pass=target_pass)
        if parser_method and inspect.ismethod(parser_method):
            return parser_method(respond_bytes)
        
        if self.log_before_resp_parsing:
            print(f"Response: {respond_bytes}")
        
        the_err = None
        respond_decrypted = xor_decrypt(respond_bytes)
        j_value = json.loads(respond_decrypted)
        if not j_value or not j_value['status']:
            if j_value['data']['code'] != 0:
                the_err = await self.get_error_by_code(
                    req_path=req_data,
                    error_code=j_value['data']['code'],
                    response=respond_bytes,
                )
                
                if not no_err_handling and isinstance(the_err, Exception):
                    raise the_err
                    
            if not no_err_handling:
                raise UnknownError(f"Unknown error occurred for {req_path}", respond_bytes)
        
        api_response: APIResponse = APIResponse(j_value)
        api_response.the_err = the_err
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
        
    async def aclose(self):
        try:
            return await self.http_client.aclose()
        except: pass
    
    @staticmethod
    def generate_passport() -> str:
        return ''.join(random.choices("abcdef0123456789", k=_MAX_PASSPORT_LENGTH))
    

