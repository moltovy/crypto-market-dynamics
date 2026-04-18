"""CryptoQuant Research — Python package.

Public surface:
    - cqresearch.data      : CSV loaders, calendar utilities, missingness taxonomy, panel builders
    - cqresearch.features  : factor library per block (macro / institutional / liquidity / btc_native / eth_native)
    - cqresearch.modeling  : static/rolling OLS, partial R^2, structural breaks, VAR/FEVD, event study, vol models
    - cqresearch.analysis  : orchestrators gluing features + models into panel-level tables
    - cqresearch.viz       : plotting palette, rcParams, helpers, figure templates
    - cqresearch.utils     : io, logging, hashing, config loader, citation helpers
"""

__version__ = "0.1.0"
