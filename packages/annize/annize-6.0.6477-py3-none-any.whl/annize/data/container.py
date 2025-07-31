# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only


class Basket(list):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_annize_basket = True
