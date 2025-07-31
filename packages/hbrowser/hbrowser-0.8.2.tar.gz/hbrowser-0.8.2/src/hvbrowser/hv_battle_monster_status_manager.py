from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver, WebElement

from .hv import HVDriver


# Debuff 名稱對應圖示檔名
BUFF_ICON_MAP = {
    "Imperil": ["imperil.png"],
    "Weaken": ["weaken.png"],
    "Blind": ["blind.png"],
    "Slow": ["slow.png"],
    "MagNet": ["magnet.png"],
    "Silence": ["silence.png"],
    "Drain": ["drainhp.png"],
    # 你可以繼續擴充
}


class MonsterStatusManager:
    ALIVE_MONSTER_XPATH = '//div[starts-with(@id, "mkey_") and not(.//img[@src="/y/s/nbardead.png"]) and not(.//img[@src="/isekai/y/s/nbardead.png"])]'

    def __init__(self, driver: HVDriver) -> None:
        self.hvdriver: HVDriver = driver

    @property
    def driver(self) -> WebDriver:
        return self.hvdriver.driver

    @property
    def pane_monster_webelement(self) -> WebElement:
        """Returns the pane containing monster elements."""
        return self.driver.find_element(By.ID, "pane_monster")

    @property
    def alive_monster_webelement(self) -> list[WebElement]:
        """Returns the pane containing alive monster elements."""
        return self.pane_monster_webelement.find_elements(
            By.XPATH, self.ALIVE_MONSTER_XPATH
        )

    @property
    def alive_count(self) -> int:
        """Returns the number of monsters in the battle."""
        return len(self.alive_monster_webelement)

    @property
    def alive_monster_ids(self) -> list[int]:
        """Returns a list of IDs of alive monsters in the battle."""
        return [
            int(id_.removeprefix("mkey_"))
            for el in self.alive_monster_webelement
            if (id_ := el.get_attribute("id")) is not None
        ]

    @property
    def alive_system_monster_ids(self) -> list[int]:
        """Returns a list of system monster IDs in the battle that have style attribute."""
        # 基於 ALIVE_MONSTER_XPATH 再加上有 style 設定的條件
        elements = self.pane_monster_webelement.find_elements(
            By.XPATH,
            f"({self.ALIVE_MONSTER_XPATH})[@style]",
        )
        return [
            int(id_.removeprefix("mkey_"))
            for el in elements
            if (id_ := el.get_attribute("id")) is not None
        ]

    def get_monster_ids_with_debuff(self, debuff: str) -> list[int]:
        """Returns a list of monster IDs that have the specified debuff."""
        icons = BUFF_ICON_MAP.get(debuff, [f"{debuff}.png"])
        # 支援主站與異世界圖示
        xpath_conditions = " or ".join(
            [f'@src="/y/e/{icon}" or @src="/isekai/y/e/{icon}"' for icon in icons]
        )
        xpath = f'//div[starts-with(@id, "mkey_")][.//img[{xpath_conditions}]]'
        elements = self.pane_monster_webelement.find_elements(By.XPATH, xpath)
        return [
            int(id_.removeprefix("mkey_"))
            for el in elements
            if (id_ := el.get_attribute("id")) is not None
        ]

    def get_monster_id_by_name(self, name: str) -> int:
        """
        根據怪物名稱取得對應的 monster id（如 mkey_0 會回傳 0）。
        """
        xpath = f'//div[starts-with(@id, "mkey_")][.//div[text()="{name}"]]'
        elements = self.pane_monster_webelement.find_elements(By.XPATH, xpath)
        if elements:
            id_ = elements[0].get_attribute("id")
            if id_ and id_.startswith("mkey_"):
                return int(id_.removeprefix("mkey_"))
        return -1
