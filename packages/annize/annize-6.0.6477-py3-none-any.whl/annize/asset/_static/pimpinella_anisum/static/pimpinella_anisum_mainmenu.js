/*
* SPDX-FileCopyrightText: © 2020 Josef Hahn
* SPDX-License-Identifier: AGPL-3.0-only
*/

"use strict";

document.addEventListener("DOMContentLoaded", function() {

    // NOTE: the menu should also work without javascript (at least in a minimal way)

    // NOTE: it might be hard to modify this bunch of hacks - better redesign the main menu from scratch if needed. ;)

    var menupanel = document.getElementById("menupanel");
    var menubutton = document.getElementById("menubutton");
    var menuclosepad = document.getElementById("menuclosepad");
    var menuclosepadindicator = document.getElementById("menuclosepadindicator");
    var sphinxsidebarwrapper = document.querySelector(".sphinxsidebarwrapper");
    var bodyblock = document.querySelector(".body");

    function showmenupanel() {
        document.body.classList.add("openmenu");
    }

    function hidemenupanel() {
        menupanel.addEventListener("animationend", function() {
            document.body.classList.remove("openmenu");
            document.body.classList.remove("closingmenu");
        }, { once : true });
        document.body.classList.add("closingmenu");
    }

    for (let aa of document.querySelectorAll(".sphinxsidebar a"))
        aa.addEventListener("click", hidemenupanel);
    menubutton.addEventListener("click", showmenupanel);
    menubutton.addEventListener("mousemove", showmenupanel);

    menuclosepad.addEventListener("click", hidemenupanel);

    menuclosepad.textContent = menuclosepadindicator.textContent;

    // dynamic sidebar viewport visualizer

    var sections = [];

    class Section {

        constructor(bodynode, treenode) {
            this.bodynode = bodynode;
            this.treenode = treenode;
            this.subsections = [];
        }

        get top() {
            return this.bodynode.offsetTop;
        }

        get height() {
            return (this.subsections.length == 0) ? this.bodynode.offsetHeight : 1;
        }

        addSubsection(s) {
            this.subsections.push(s);
        }

    }

    function descentSection(s, t, se) {
        var i = 0;
        for (var cs of s.children) {
            if (cs.classList.contains("section")) {
                var ct = t.children[i];
                if (ct) {
                    i++;
                    var sect = new Section(cs, ct);
                    sections.push(sect);
                    var tct = _treenode_getchildcont(ct);
                    if (tct)
                        descentSection(cs, tct, sect);
                    if (se)
                        se.addSubsection(sect);
                }
            }
        }
    }

    function rootGlobalTreeSectionNode(n) {
        var r = n.querySelectorAll(":scope > ul.current,li.current");
        return (r.length > 0) ? rootGlobalTreeSectionNode(r) : n;
    }

    var treeblock = Array.from(document.body.querySelector(".localtoc").children);
    var rootsectblock = bodyblock;
    if (treeblock.length > 0)
        treeblock = treeblock[0];
    else {
        treeblock = _treenode_getchildcont(rootGlobalTreeSectionNode(document.body.querySelector(".globaltoc")));
        rootsectblock = rootsectblock.querySelectorAll(":scope > .section");
    }
    descentSection(rootsectblock, treeblock);

    function visibleSections() {
        var scrollpos1 = bodyblock.scrollTop;
        var scrollpos2 = scrollpos1 + bodyblock.offsetHeight;
        var result = [];
        for (var s of sections) {
            var tops = s.top;
            var heights = s.height;
            var bottoms = tops + heights;
            if (tops > scrollpos2)
                break;
            else if (bottoms > scrollpos1)
                result.push(s);
        }
        return result;
    }

    var menuSectionIndicator = document.createElement("div");
    menuSectionIndicator.className = "menusectionindicator"
    sphinxsidebarwrapper.appendChild(menuSectionIndicator);

    function _treenode_getlabel(t) {
        return t.querySelector(":scope > a");
    }

    function _treenode_getchildcont(t) {
        return t.querySelector(":scope > ul");
    }

    function _refreshMenuSectionIndicator() {
        var vis = visibleSections();
        var yfrm = 0;
        var yto = 0;
        if (vis.length > 0) {
            yfrm = vis[0].treenode.offsetTop;
            yto = vis[vis.length-1].treenode.offsetTop + _treenode_getlabel(vis[vis.length-1].treenode).offsetHeight;
        }
        var yhgt = yto - yfrm;
        menuSectionIndicator.style.top = yfrm + "px";
        menuSectionIndicator.style.height = yhgt + "px";
        if (yto > 0) {
            var pd = Math.max(0, (sphinxsidebarwrapper.offsetHeight - yhgt) / 2);
            scrollToMenuSectionIndicator(yfrm - pd);
        }
    }

    var _scrollToMenuSectionIndicator_pos = 0;

    var _scrollToMenuSectionIndicator_scrolling = false;

    function _processScrollToMenuSectionIndicator() {
        _scrollToMenuSectionIndicator_scrolling = true;
        var d = _scrollToMenuSectionIndicator_pos - sphinxsidebarwrapper.scrollTop;
        d = Math.min(Math.max(d, -6), 6);
        if (d) {
            sphinxsidebarwrapper.scrollTop += d;
            setTimeout(_processScrollToMenuSectionIndicator, 5);
        }
        else
            _scrollToMenuSectionIndicator_scrolling = false;
    }

    function scrollToMenuSectionIndicator(v) {
        _scrollToMenuSectionIndicator_pos = Math.max(0, parseInt(v));
        if (!_scrollToMenuSectionIndicator_scrolling)
            _processScrollToMenuSectionIndicator();
    }

    var _refreshMenuSectionIndicator_busy = false;
    var _refreshMenuSectionIndicator_doagain = false;

    function refreshMenuSectionIndicator() {
        if (_refreshMenuSectionIndicator_busy)
            _refreshMenuSectionIndicator_doagain = true;
        else {
            _refreshMenuSectionIndicator_busy = true;
            _refreshMenuSectionIndicator();
            setTimeout(function(){
                _refreshMenuSectionIndicator_busy = false;
                if (_refreshMenuSectionIndicator_doagain) {
                    _refreshMenuSectionIndicator_doagain = false;
                    refreshMenuSectionIndicator();
                }
            }, 1000);
        }
    }

    bodyblock.addEventListener("scroll", refreshMenuSectionIndicator);
    refreshMenuSectionIndicator();

});
