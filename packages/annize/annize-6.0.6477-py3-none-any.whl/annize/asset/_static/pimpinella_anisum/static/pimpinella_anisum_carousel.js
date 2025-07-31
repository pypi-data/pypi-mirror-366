/*
* SPDX-FileCopyrightText: © 2020 Josef Hahn
* SPDX-License-Identifier: AGPL-3.0-only
*/

"use strict";

class AnnizeDoc_ImageCarousel {

    _resize() {
        var mheight = 0;
        for(var i=0; i<this.imagenodes.length; i++)
            mheight = Math.max(mheight, this.imagenodes[i].offsetHeight);
        this.rootnode.style.height = (mheight + this.carousel.offsetHeight) + "px";
    }

    showitem(no, _skipresetswitch) {
        var self = this;
        if (no == this.currentitem)
            return;
        for(var i=0; i<this.imagenodes.length; i++) {
            var inode = this.imagenodes[i];
            if (i == no) {
                inode.style.opacity = 1;
                inode.style.zIndex = 1;
                inode.ilnk.className = inode.ilnk.origClassName + " current";
            }
            else {
                inode.style.opacity = 0;
                inode.style.zIndex = 0;
                inode.ilnk.className = inode.ilnk.origClassName;
            }
        }
        if (this.currentitem !== undefined) {
            var cn = this.imagenodes[this.currentitem];
            if (cn._stop)
                cn._stop();
        }
        this.currentitem = no;
        if (!_skipresetswitch)
            this._resetSwitchNextInterval();
    }

    constructor(rootnode) {
        var self = this;
        this.rootnode = rootnode;
        this.imagenodes = Array.from(rootnode.children);
        this.carousel = document.createElement("div");
        this.carousel.className = "carousel";
        if (this.imagenodes.length < 2)
            return;
        this.rootnode.style.position = "relative";
        this.rootnode.appendChild(this.carousel);
        for(var i=0; i<this.imagenodes.length; i++) {
            var inode = this.imagenodes[i];
            if (inode._registerloadhandler)
                inode._registerloadhandler(function(){ self._resize(); });
            inode.className += " childitem";
            var ilnk = document.createElement("span");
            ilnk.textContent = "⑩";
            if (i % 10 == 9)
                ilnk.className = "fullten";
            ilnk.onclick = (function(ii) { return function(e) { self.showitem(ii); }; })(i);
            this.carousel.appendChild(ilnk);
            inode.ilnk = ilnk;
            ilnk.origClassName = ilnk.className;
        }
        var nxtlnk = document.createElement("span");
        nxtlnk.textContent = "〉";
        nxtlnk.className = "next";
        nxtlnk.onclick = function() { self.nextitem(); };
        this.carousel.appendChild(nxtlnk);
        var oonresize = window.onresize;
        window.onresize = function() {
            self._resize();
            if (oonresize)
                oonresize();
        }
        this._resize();
        this.showitem(0, true);
        this._initintid = setInterval(function(){
            var r = rootnode.getBoundingClientRect();
            if (r.bottom > 0 && r.top < window.innerHeight) {
                clearInterval(self._initintid);
                self._resetSwitchNextInterval();
            }
        }, 2000);
        rootnode.addEventListener("touchstart", function(event) {
            self._touchbeginpos = undefined;
            var ino = self.imagenodes[self.currentitem];
            if (ino._isactive && ino._isactive())
                return;
            if (event.changedTouches.length == 1) {
                self._touchbeginpos = event.changedTouches[0];
                self._touchbegintime = Date.now();
            }
        }, false);
        rootnode.addEventListener("touchend", function(event) {
            if (self._touchbeginpos) {
                if (Date.now()-self._touchbegintime < 600 && event.changedTouches.length == 1) {
                    var pos1 = self._touchbeginpos;
                    var pos2 = event.changedTouches[0];
                    var dx = pos2.clientX - pos1.clientX;
                    var dy = pos2.clientY - pos1.clientY;
                    var adx = Math.abs(dx);
                    var ady = Math.abs(dy);
                    if (ady < 60 && adx > 40 && adx > ady)
                        self.nextitem(dx > 0);
                }
                self._touchbeginpos = undefined;
            }
        }, false);
    }

    _resetSwitchNextInterval() {
        var self = this;
        if (this._switchnextintid !== undefined)
            clearInterval(this._switchnextintid);
        this._switchnextintid = setInterval(function() {
            var ino = self.imagenodes[self.currentitem];
            if (!ino._isactive || !ino._isactive())
                self.nextitem();
        }, 9000);
    }

    nextitem(prev) {
        this.showitem((this.currentitem+(prev?-1:1)+this.imagenodes.length) % this.imagenodes.length);
    }

}

document.addEventListener("DOMContentLoaded", function() {
    for (let nod of document.body.querySelectorAll(".annizedoc-mediagallery")) {
        for (let noda of nod.querySelectorAll("a")) {
            var ih = noda.href.lastIndexOf("#");
            var imgtype = noda.href.substring(ih+1);
            var src = noda.href.substring(0, ih);
            var parentNode = noda.parentNode;
            var labeltext = noda.textContent;
            parentNode.removeChild(noda);
            var hostnode = document.createElement("div");
            hostnode.style.position = "absolute";
            parentNode.appendChild(hostnode);
            if (imgtype == "image") {
                var piece = document.createElement("img");
                piece.src = src;
                piece.style.cursor = "pointer";
                piece.addEventListener("click", function(){
                    window.open(piece.src, "_blank");
                });
                hostnode._registerloadhandler = function(h) {
                    piece.addEventListener("load", h);
                }
            }
            else if (imgtype == "video") {
                var piece = document.createElement("video");
                piece.preload = "metadata";
                piece.src = src;
                piece.controls = true;
                hostnode._stop = function() {
                    piece.pause();
                };
                hostnode._isactive = function() {
                    return !piece.paused;
                }
                hostnode._registerloadhandler = function(h) {
                    piece.addEventListener("loadedmetadata", h);
                }
            }
            if (piece) {
                piece.className = "mediagallerypiece";
                hostnode.appendChild(piece);
            }
            var lbl = document.createElement("div");
            lbl.textContent = labeltext;
            hostnode.appendChild(lbl);
        }
        new AnnizeDoc_ImageCarousel(nod);
        nod.style.visibility = "hidden";
        var self = nod;
        setTimeout(function(){ self.style.visibility = "inherit"; }, 2000);
    }
}, false);
