from pydantic import BaseModel
from .utils import xor_encrypt
from typing import (
    Any, List, Dict, Optional
)
import time

class IntArray(str):
    pass

LeagueWinnerRanges = Dict[str, int]

class LoadRequestDefaults:
	DEFAULT_GAME_VERSION      = "1.9.10691"
	DEFAULT_U_DID             = "a341224a6fa458c8"
	DEFAULT_OS_TYPE           = 2
	DEFAULT_OS_VERSION        = "7.1.2"
	DEFAULT_PHONE_MODEL       = "google pixel 2"
	DEFAULT_METRIX_UID        = "-"
	DEFAULT_APPS_FLYER_UID     = "1686402669312-333768616178664406"
	DEFAULT_DEVICE_NAME       = "unknown"
	DEFAULT_CONSTANTS_VERSION = "142"
	DEFAULT_STORE_TYPE        = "myket"
	DEFAULT_CLIENT_VALUE      = "iOS"
	DEFAULT_LANG_VALUE        = "fa-IR"

def new_int_array(values: List[Any]) -> IntArray:
    output = "["
    for i, current in enumerate(values):
        output += str(current)

        if i != len(values)-1:
            output += ","
    
    output += "]"
    return IntArray(output)
    

class Scaffold():
    def get_action(self) -> str:
        pass
    
    

class DScaffold(Scaffold, BaseModel):
    """
    DScaffold is a base class for all data classes that need to be sent to the server.
    """
    pass
    
    def get_response_type(self) -> type:
        pass
    
    def get_serialized(self, key: str = None):
        return xor_encrypt(self.json(), key=key)

class APIResponse:
    status: Optional[bool] = False
    code: Optional[int] = 0
    data: DScaffold = None
    arguments: Optional[Any] = None
    
    def __init__(self, j_value: dict) -> None:
        if not isinstance(j_value, dict):
            raise TypeError("j_value must be a dict")
        
        self.status = j_value.get('status', False)
        self.arguments = j_value.get('arguments', None)


class CardInfo(DScaffold):
    type: Optional[int] = 0
    cards: Optional[Any] = None
    card_pack_type: int = int

class AttackCardInfo(DScaffold):
    id: Optional[int] = 0
    last_used_at: Optional[int] = 0
    power: Optional[int] = 0
    base_card_id: Optional[int] = 0
    player_id: Optional[int] = 0
    internal_last_time_used: Optional[int] = 0

    def set_as_used(self):
        self.internal_last_time_used = time.time()


class QuestResponse(DScaffold):
    code: Optional[int] = 0
    arguments: Optional[List[Any]] = []
    outcome: Optional[bool] = False
    boss_mode: Optional[bool] = False
    gold: Optional[int] = 0
    gold_added: Optional[int] = 0
    level_up_gold_added: Optional[int] = 0
    xp: Optional[int] = 0
    xp_added: Optional[int] = 0
    rank: Optional[int] = 0
    tribe_rank: Optional[int] = 0
    attack_cards: Optional[List[AttackCardInfo]] = []
    tribe_gold: Optional[int] = 0
    # gift_card: Optional[Any] = None
    q: Optional[int] = 0
    total_quests: Optional[int] = 0
    needs_captcha: Optional[bool] = False
    league_id: Optional[int] = 0
    # tutorial_required_cards: Optional[Any] = None
    potion_number: Optional[int] = 0
    nectar: Optional[int] = 0
    
    raw_response: Optional[bytes] = b""



class Onsale(DScaffold):
    num1: Optional[List[int]] = None
    num2: Optional[List[int]] = None
    num3: Optional[List[int]] = None
    num4: Optional[List[int]] = None
    num7: Optional[List[int]] = None
    num8: Optional[List[int]] = None
    num10: Optional[List[int]] = None
    num12: Optional[List[int]] = None
    num13: Optional[List[int]] = None
    num14: Optional[List[int]] = None


class Price(DScaffold):
    num1: Optional[str] = ""
    num2: Optional[str] = ""
    num3: Optional[str] = ""
    num4: Optional[str] = ""
    num7: Optional[str] = ""
    num8: Optional[str] = ""
    num10: Optional[str] = ""
    num12: Optional[str] = ""
    num13: Optional[str] = ""
    num14: Optional[str] = ""

class GoldPackInfo(DScaffold):
    name: str = ''
    price: Price = None
    gold_amount: Optional[int] = 0
    gold_to_price_ratio: Optional[float] = 0.0
    product_uid: str = ''
    gives_avatar: Optional[bool] = False
    popularity: Optional[int] = 0
    onsale: Onsale = None

class ModulesVersion(DScaffold):
    Constants: Optional[str] = ""
    TutorialData: Optional[int] = 0
    TutorialLanguage_en: Optional[int] = 0
    TutorialLanguage_fa: Optional[int] = 0
    CardComboData: Optional[int] = 0
    CardComboLanguage_en: Optional[int] = 0
    CardComboLanguage_fa: Optional[int] = 0
    BaseHeroItems: Optional[int] = 0
    BaseHeroItemsLanguage_en: Optional[int] = 0
    BaseHeroItemsLanguage_fa: Optional[int] = 0
    BaseFruitLanguage_fa: Optional[int] = 0
    BaseFruitLanguage_en: Optional[int] = 0


class Coaching(DScaffold):
    trained_players: Optional[int] = 0

class DailyReward(DScaffold):
    next_reward_at: Optional[int] = 0



class Bundles(DScaffold):
    id: Optional[int] = 0
    description: Optional[str] = ""
    gold_pack_info: GoldPackInfo = None
    gold_amount: Optional[int] = 0
    nectar_amount: Optional[int] = 0
    fill_potion: Optional[bool] = False
    boost_pack_type: Optional[int] = 0
    card_info: CardInfo = None
    rewards_count: Optional[int] = 0
    duration: Optional[int] = 0
    start_date: Optional[int] = 0
    end_date: Optional[int] = 0
    max_level: Optional[int] = 0
    min_level: Optional[int] = 0
    show_on_home: Optional[bool] = False
    discount_ratio: Optional[float] = 0.0


class HeroItemInfo(DScaffold):
    id: Optional[int] = 0
    base_heroitem_id: Optional[int] = 0
    state: Optional[int] = 0
    position: Optional[int] = 0

class HeroIDSet(DScaffold):
    items: Optional[List[HeroItemInfo]] = None
    id: Optional[int] = 0
    power: Optional[int] = 0
    base_card_id: Optional[int] = 0
    potion: Optional[int] = 0

class HeroItems(DScaffold):
    id: Optional[int] = 0
    base_heroitem_id: Optional[int] = 0
    base_hero_id: Optional[int] = 0
    used_count: Optional[int] = 0
    state: Optional[int] = 0
    position: Optional[int] = 0


class Achievements(DScaffold):
    player_id: Optional[int] = 0
    achievement_id: Optional[int] = 0
    created_at: Optional[int] = 0
    id: Optional[int] = 0


class Tribe(DScaffold):
    id: Optional[int] = 0
    name: Optional[str] = ""
    description: Optional[str] = ""
    score: Optional[int] = 0
    rank: Optional[int] = 0
    gold: Optional[int] = 0
    member_count: Optional[int] = 0
    defense_building_level: Optional[int] = 0
    offense_building_level: Optional[int] = 0
    cooldown_building_level: Optional[int] = 0
    mainhall_building_level: Optional[int] = 0
    donates_number: Optional[int] = 0
    status: Optional[int] = 0
    weekly_score: Optional[int] = 0
    weekly_rank: Optional[int] = 0


class FruitCardInfo(DScaffold):
    id: Optional[int] = 0
    name: Optional[str] = ""
    small_image: Optional[str] = ""
    max_level: Optional[int] = 0
    min_level: Optional[int] = 0
    category: Optional[int] = 0
    description: Optional[str] = ""
    

class PlayerLoadResponse(DScaffold):
    code: Optional[int] = 0
    id: Optional[int] = 0
    name: Optional[str] = ""
    rank: Optional[int] = 0
    league_rank: Optional[int] = 0
    xp: Optional[int] = 0
    weekly_score: Optional[int] = 0
    level: Optional[int] = 0
    def_power: Optional[int] = 0
    league_id: Optional[int] = 0
    gold: Optional[int] = 0
    tribe_permission: Optional[int] = 0
    gold_building_level: Optional[int] = 0
    bank_building_level: Optional[int] = 0
    new_messages: Optional[int] = 0
    restore_key: Optional[str] = ""
    invite_key: Optional[str] = ""
    needs_captcha: Optional[bool] = False
    cooldowns_bought_today: Optional[int] = 0
    total_quests: Optional[int] = 0
    total_battles: Optional[int] = 0
    q: Optional[int] = 0
    bank_account_balance: Optional[int] = 0
    last_gold_collect_at: Optional[int] = 0
    tutorial_id: Optional[int] = 0
    tutorial_index: Optional[int] = 0
    potion_number: Optional[int] = 0
    nectar: Optional[int] = 0
    hero_id: Optional[int] = 0
    birth_year: Optional[int] = 0
    gender: Optional[int] = 0
    phone: Optional[str] = ""
    address: Optional[str] = ""
    realname: Optional[str] = ""
    prev_league_id: Optional[int] = 0
    prev_league_rank: Optional[int] = 0
    won_battle_num: Optional[int] = 0
    lost_battle_num: Optional[int] = 0
    mood_id: Optional[int] = 0
    avatar_id: Optional[int] = 0
    updated_at: Optional[int] = 0
    last_load_at: Optional[int] = 0
    medals: Optional[Any] = None
    avatar_slots: Optional[int] = 0
    avatars: Optional[List[str]] = []
    owned_avatars: Optional[List[int]] = []
    activity_status: Optional[int] = 0
    has_email: Optional[bool] = False
    cards: Optional[List[AttackCardInfo]] = []
    gold_building_assigned_cards: Optional[List[AttackCardInfo]] = []
    offense_building_assigned_cards: Optional[List[Any]] = []
    defense_building_assigned_cards: Optional[List[Any]] = []
    auction_building_assigned_cards: Optional[List[Any]] = []
    gold_collection_allowed: Optional[bool] = False
    gold_collection_allowed_at: Optional[int] = 0
    gold_collection_extraction: Optional[int] = 0
    collection: Optional[List[int]] = []
    cards_view: Optional[int] = 0
    tribe: Tribe = None
    achievements: Optional[List[Achievements]] = []
    achievements_blob: Optional[str] = ""
    now: Optional[int] = 0
    league_remaining_time: Optional[int] = 0
    bonus_remaining_time: Optional[float] = 0.0
    is_existing_player: Optional[bool] = False
    is_name_temp: Optional[bool] = False
    sale_info: Optional[List[Any]] = []
    heroitems: Optional[List[HeroItems]] = []
    base_hero_id: Optional[int] = 0
    hero_id_set: Optional[List[HeroIDSet]] = []
    hero_max_rarity: Optional[int] = 0
    available_combo_id_set: Optional[List[int]] = []
    potion_price: Optional[int] = 0
    nectar_price: Optional[int] = 0
    better_vitrin_promotion: Optional[bool] = False
    can_use_vitrin: Optional[bool] = False
    can_watch_advertisment: Optional[bool] = False
    purchase_deposits_to_bank: Optional[bool] = False
    advertisment_provider: Optional[int] = 0
    advertisment_providers_waterfall: Optional[List[int]] = []
    advertisment_providers_random: Optional[List[int]] = []
    better_choose_deck: Optional[bool] = False
    better_quest_map: Optional[bool] = False
    better_battle_outcome_navigation: Optional[bool] = False
    better_tutorial_background: Optional[bool] = False
    better_tutorial_steps: Optional[bool] = False
    more_xp: Optional[bool] = False
    better_gold_pack_multiplier: Optional[bool] = False
    better_gold_pack_ratio: Optional[bool] = False
    better_gold_pack_ratio_on_price: Optional[bool] = False
    better_league_tutorial: Optional[bool] = False
    better_enhance_tutorial: Optional[bool] = False
    better_mine_building_status: Optional[bool] = False
    is_mine_building_limited: Optional[bool] = False
    retouched_tutorial: Optional[bool] = False
    better_card_graphic: Optional[bool] = False
    durable_buildings_name: Optional[bool] = False
    show_task_until_levelup: Optional[bool] = False
    better_restore_button_label: Optional[bool] = False
    better_quest_tutorial: Optional[bool] = False
    hero_tutorial_at_first: Optional[bool] = False
    hero_tutorial_at_first_and_selected: Optional[bool] = False
    hero_tutorial_at_first_and_selected_and_animated: Optional[bool] = False
    hero_tutorial_at_level_four: Optional[bool] = False
    hero_tutorial_at_second_quest: Optional[bool] = False
    fall_background: Optional[bool] = False
    unified_gold_icon: Optional[bool] = False
    send_all_tutorial_steps: Optional[bool] = False
    rolling_gold: Optional[bool] = False
    bundles: Optional[List[Bundles]] = []
    daily_reward: Optional[Any] = None
    coach_info: Optional[List[Any]] = []
    coaching: Optional[Coaching] = None
    coach_test: Optional[bool] = False
    mobile_number_verified: Optional[bool] = False
    wheel_of_fortune_opens_in: Optional[int] = 0
    wheel_of_fortune: Optional[bool] = False
    latest_app_version: Optional[str] = ""
    latest_app_version_for_notice: Optional[str] = ""
    latest_constants_version: Optional[str] = ""
    modules_version: ModulesVersion = None
    emergency_message: Optional[str] = ""
    update_message: Optional[str] = ""
    

PlayerMedals: Dict[str, int] = dict
ErrorMessages: Dict[str, str] = dict
DeviceConstants: Dict[str, Any] = dict
FruitExportContainer: Dict[str, FruitCardInfo] = dict



class DeviceConstantsRequest(DScaffold):
    game_version: Optional[str] = ""
    os_version: Optional[str] = ""
    model: Optional[str] = ""
    constant_version: Optional[str] = ""
    store_type: Optional[str] = ""
    
    def set_default_values(self):
        if not self.game_version:
            self.game_version = LoadRequestDefaults.DEFAULT_GAME_VERSION
        
        if not self.os_version:
            self.os_version = LoadRequestDefaults.DEFAULT_OS_VERSION
        
        if not self.model:
            self.model = LoadRequestDefaults.DEFAULT_PHONE_MODEL
        
        if not self.constant_version:
            self.constant_version = LoadRequestDefaults.DEFAULT_CONSTANTS_VERSION
        
        if not self.store_type:
            self.store_type = LoadRequestDefaults.DEFAULT_STORE_TYPE


class PlayerLoadRequest(DScaffold):
    game_version: Optional[str] = ""
    udid: Optional[str] = ""
    os_type: Optional[int] = 0
    restore_key: Optional[str] = ""
    os_version: Optional[str] = ""
    model: Optional[str] = ""
    metrix_uid: Optional[str] = ""
    appsflyer_uid: Optional[str] = ""
    device_name: Optional[str] = ""
    store_type: Optional[str] = ""
    
    def set_default_values(self):
        if not self.game_version:
            self.game_version = LoadRequestDefaults.DEFAULT_GAME_VERSION
        
        if not self.udid:
            self.udid = LoadRequestDefaults.DEFAULT_U_DID
        
        if not self.os_type:
            self.os_type = LoadRequestDefaults.DEFAULT_OS_TYPE
        
        if not self.os_version:
            self.os_version = LoadRequestDefaults.DEFAULT_OS_VERSION
        
        if not self.model:
            self.model = LoadRequestDefaults.DEFAULT_PHONE_MODEL
        
        if not self.metrix_uid:
            self.metrix_uid = LoadRequestDefaults.DEFAULT_METRIX_UID
        
        if not self.appsflyer_uid:
            self.appsflyer_uid = LoadRequestDefaults.DEFAULT_APPS_FLYER_UID
        
        if not self.device_name:
            self.device_name = LoadRequestDefaults.DEFAULT_DEVICE_NAME
        
        if not self.store_type:
            self.store_type = LoadRequestDefaults.DEFAULT_STORE_TYPE


class LanguagePathResponse(DScaffold):
    en: Dict[str, str] = {}
    fa: Dict[str, str] = {}


class PlayerComebackRequest(DScaffold):
    client: Optional[str] = ""
    
class FruitJsonExportRequest(DScaffold):
    client: Optional[str] = ""

class LanguagePatchRequest(DScaffold):
    client: Optional[str] = ""

class ErrorMessagesRequest(DScaffold):
    lang_id: Optional[str] = ""
    
    def set_default_values(self):
        if not self.lang_id:
            self.lang_id = LoadRequestDefaults.DEFAULT_LANG_VALUE

class CardsSelection():
    cards: List[int] = None
    hero_id: int = 0
    
    # NoHeal indicates we shouldn't be trying to heal any of
    # the cards. This means we are 100% sure that they have already
    # been healed previously.
    no_heal: bool = False
    
    def __init__(self, cards: List[int], hero_id: int = 0, no_heal: bool = False) -> None:
        self.cards = cards
        self.hero_id = hero_id
        self.no_heal = no_heal


class QuestRequest(DScaffold):
    cards: IntArray = []
    hero_id: Optional[int] = 0
    check: Optional[str] = ""
    _cards_selection: Optional[CardsSelection] = None


class TribeMemberInfo(DScaffold):
    id: Optional[int] = 0
    name: Optional[str] = ""
    rank: Optional[int] = 0
    exp: Optional[int] = 0
    gold: Optional[int] = 0
    tribe_permission: Optional[int] = 0
    level: Optional[int] = 0
    def_power: Optional[int] = 0
    status: Optional[int] = 0
    league_id: Optional[int] = 0
    league_rank: Optional[int] = 0
    avatar_id: Optional[int] = 0
    poke_status: Optional[bool] = False


class OpponentInfo(DScaffold):
    id: Optional[int] = 0
    name: Optional[str] = ""
    rank: Optional[int] = 0
    exp: Optional[int] = 0
    gold: Optional[int] = 0
    tribe_permission: Optional[int] = 0
    level: Optional[int] = 0
    def_power: Optional[int] = 0
    status: Optional[int] = 0
    league_id: Optional[int] = 0
    league_rank: Optional[int] = 0
    avatar_id: Optional[int] = 0
    power_ratio: Optional[int] = 0
    tribe_name: Optional[str] = ""


class BattleResponse(DScaffold):
    code: Optional[int] = 0
    outcome: Optional[bool] = False
    won_by_chance: Optional[bool] = False
    gold: Optional[int] = 0
    gold_added: Optional[int] = 0
    league_bonus: Optional[int] = 0
    levelup_gold_added: Optional[int] = 0
    level: Optional[int] = 0
    exp: Optional[int] = 0
    exp_added: Optional[int] = 0
    rank: Optional[int] = 0
    tribe_rank: Optional[int] = 0
    attack_cards: Optional[List[AttackCardInfo]] = []
    opponent_cards: Optional[List[AttackCardInfo]] = []
    tribe_gold: Optional[int] = 0
    gift_card: Optional[Any] = None
    attack_power: Optional[float] = 0.0
    def_power: Optional[float] = 0.0
    q: Optional[int] = 0
    total_battles: Optional[int] = 0
    needs_captcha: Optional[bool] = False
    league_rank: Optional[int] = 0
    league_id: Optional[int] = 0
    weekly_score: Optional[int] = 0
    score_added: Optional[int] = 0
    won_battle_num: Optional[int] = 0
    lost_battle_num: Optional[int] = 0
    attack_bonus_power: Optional[float] = 0.0
    def_bonus_power: Optional[float] = 0.0
    tutorial_required_cards: Optional[Any] = None
    attacker_combo_info: Optional[List[Any]] = []
    defender_combo_info: Optional[List[Any]] = []
    potion_number: Optional[int] = 0
    nectar: Optional[int] = 0
    gift_potion: Optional[int] = 0
    gift_nectar: Optional[int] = 0
    available_combo_id_set: Optional[Any] = None
    purchase_deposits_to_bank: Optional[Any] = None
    attacker_hero_benefits_info: Optional[List[Any]] = []
    defender_hero_benefits_info: Optional[List[Any]] = []
    raw_response: Optional[bytes] = b""


class BattleRequest(DScaffold):
    opponent_id: Optional[int] = 0
    check: Optional[str] = ""
    cards: Optional[IntArray] = None
    hero_id: Optional[int] = 0
    attacks_in_today: Optional[int] = 0
    _cards_selection: Optional[CardsSelection] = None


class GetOpponentsResponse(DScaffold):
    players: Optional[List[OpponentInfo]] = []


class GetOpponentsRequest(DScaffold):
    client: Optional[str] = ""
    _other_pass: Optional[str] = ""

class TribeMembersResponse(DScaffold):
    members: Optional[List[TribeMemberInfo]] = []


class TribeMembersRequest(DScaffold):
    coach_tribe: Optional[bool] = False
    

class CoolOffResponse(DScaffold):
    code: Optional[int] = 0
    gold: Optional[int] = 0
    cooldowns_bought_today: Optional[int] = 0



class CoolOffRequest(DScaffold):
    card_id: Optional[int] = 0


class LiveBattleResponse(DScaffold):
    code: Optional[int] = 0
    arguments: Optional[Any] = None
    battle_id: Optional[int] = 0
    help_cost: Optional[int] = 0


class LiveBattleRequest(DScaffold):
    opponent_id: Optional[int] = 0


class SetCardForLiveBattleResponse(DScaffold):
    last_used_at: Optional[int] = 0


class SetCardForLiveBattleRequest(DScaffold):
    round: Optional[int] = 0
    card: Optional[int] = 0
    battle_id: Optional[int] = 0

class TribeInfo(DScaffold):
    id: Optional[int] = 0
    name: Optional[str] = ""
    description: Optional[str] = ""
    score: Optional[int] = 0
    rank: Optional[int] = 0
    member_count: Optional[int] = 0
    weekly_score: Optional[int] = 0
    weekly_rank: Optional[int] = 0


class TribeRankingsResponse(DScaffold):
    top_tribes: Optional[List[TribeInfo]] = []
    near_tribes: Optional[List[TribeInfo]] = []
    tribe_rank: Optional[int] = 0


class TribeRankingsRequest(DScaffold):
    client: Optional[str] = ""


class LiveBattleHelpRequest(DScaffold):
    battle_id: Optional[int] = 0

class PlayerRankingInfo(DScaffold):
    id: Optional[int] = 0
    name: Optional[str] = ""
    rank: Optional[int] = 0
    exp: Optional[int] = 0
    level: Optional[int] = 0
    tribe_id: Optional[int] = 0
    tribe_name: Optional[str] = ""
    avatar_id: Optional[int] = 0


class GlobalRankingsResponse(DScaffold):
    top_players: Optional[List[PlayerRankingInfo]] = []
    near_players: Optional[List[PlayerRankingInfo]] = []
    rank: Optional[int] = 0


class GlobalRankingsRequest(DScaffold):
    client: Optional[str] = ""


class PlayerLeagueRankingInfo(DScaffold):
    id: Optional[int] = 0
    name: Optional[str] = ""
    league_rank: Optional[int] = 0
    overall_score: Optional[int] = 0
    weekly_score: Optional[int] = 0
    level: Optional[int] = 0
    tribe_id: Optional[int] = 0
    tribe_name: Optional[str] = ""
    avatar_id: Optional[int] = 0


class LeagueRankingsResponse(DScaffold):
    top_players: Optional[List[PlayerLeagueRankingInfo]] = []
    near_players: Optional[List[PlayerLeagueRankingInfo]] = []
    league_rank: Optional[int] = 0
    winner_ranges: LeagueWinnerRanges = None
    league_rising_rank: Optional[int] = 0
    league_falling_rank: Optional[int] = 0
    current_league_bonus: Optional[int] = 0
    next_league_bonus: Optional[int] = 0


class FillPotionRequest(DScaffold):
    amount: Optional[int] = 0


class FillPotionResponse(DScaffold):
    code: Optional[int] = 0
    added_potion: Optional[int] = 0
    potion_number: Optional[int] = 0
    gold: Optional[int] = 0


class PotionizeRequest(DScaffold):
    potion: Optional[int] = 0
    hero_id: Optional[int] = 0


class PotionizeResponse(DScaffold):
    code: Optional[int] = 0
    player_potion: Optional[int] = 0
    nectar: Optional[int] = 0
    gold: Optional[int] = 0
    hero_potion: Optional[int] = 0


class GetPlayerInfoRequest(DScaffold):
    player_id: Optional[int] = 0


class GetPlayerInfoResponse(DScaffold):
    code: Optional[int] = 0
    name: Optional[str] = ""
    total_rank: Optional[int] = 0
    won_battle_num: Optional[int] = 0
    lost_battle_num: Optional[int] = 0
    mood_id: Optional[int] = 0
    avatar_id: Optional[int] = 0
    updated_at: Optional[int] = 0
    last_load_at: Optional[int] = 0
    tribe_name: Optional[str] = ""
    tribe_rank: Optional[int] = 0
    tribe_position: Optional[int] = 0
    league_id: Optional[int] = 0
    league_rank: Optional[int] = 0
    prev_league_id: Optional[int] = 0
    medals: Optional[Any] = None


class LeagueRankingsRequest(DScaffold):
    client: Optional[str] = ""
