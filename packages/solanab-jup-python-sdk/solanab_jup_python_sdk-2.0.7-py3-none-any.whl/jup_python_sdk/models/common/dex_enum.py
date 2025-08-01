from enum import Enum
from urllib.parse import quote


class DexEnum(str, Enum):
    """
    Enumeration of supported DEXes (Decentralized Exchanges) on Jupiter.

    Each value represents a different liquidity source that Jupiter can route through.
    The string values are URL-encoded when used in API requests.
    """

    WOOFI = "Woofi"
    PUMP_FUN = "Pump.fun"
    WHIRLPOOL = "Whirlpool"
    VIRTUALS = "Virtuals"
    DAOS_FUN = "Daos.fun"
    LIFINITY_V2 = "Lifinity V2"
    STABBLE_STABLE_SWAP = "Stabble Stable Swap"
    TOKEN_MILL = "Token Mill"
    METEORA = "Meteora"
    OASIS = "Oasis"
    ALDRIN = "Aldrin"
    GOOSEFX_GAMMA = "GooseFX GAMMA"
    PERPS = "Perps"
    SOLFI = "SolFi"
    DEXLAB = "DexLab"
    TOKEN_SWAP = "Token Swap"
    ZEROFI = "ZeroFi"
    CROPPER = "Cropper"
    OBRIC_V2 = "Obric V2"
    STABBLE_WEIGHTED_SWAP = "Stabble Weighted Swap"
    SANCTUM_INFINITY = "Sanctum Infinity"
    MOONIT = "Moonit"
    SANCTUM = "Sanctum"
    RAYDIUM_CP = "Raydium CP"
    PHOENIX = "Phoenix"
    PUMP_FUN_AMM = "Pump.fun Amm"
    SABER = "Saber"
    SABER_DECIMALS = "Saber (Decimals)"
    RAYDIUM_CLMM = "Raydium CLMM"
    DEX_1 = "1DEX"
    PENGUIN = "Penguin"
    ORCA_V2 = "Orca V2"
    FLUXBEAM = "FluxBeam"
    RAYDIUM = "Raydium"
    METEORA_DLMM = "Meteora DLMM"
    BONKSWAP = "Bonkswap"
    SOLAYER = "Solayer"
    STEPN = "StepN"
    HELIUM_NETWORK = "Helium Network"
    MERCURIAL = "Mercurial"
    PERENA = "Perena"
    ORCA_V1 = "Orca V1"
    ALDRIN_V2 = "Aldrin V2"
    SAROS = "Saros"
    OPENBOOK_V2 = "OpenBook V2"
    CREMA = "Crema"
    OPENBOOK = "Openbook"
    INVARIANT = "Invariant"
    GUACSWAP = "Guacswap"

    def __str__(self) -> str:
        """
        Return URL-encoded string representation of the DEX name.

        Returns:
            URL-encoded DEX name suitable for API requests.
        """
        return quote(self.value)
