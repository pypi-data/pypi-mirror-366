/*
* SPDX-FileCopyrightText: © 2020 Josef Hahn
* SPDX-License-Identifier: AGPL-3.0-only
*/

"use strict";

document.addEventListener("DOMContentLoaded", function() {
    for (let externalLink of document.body.querySelectorAll(".body a:not([class*=internal])"))
        externalLink.target = "_blank";

    document.body.classList.add("scripted");
});
