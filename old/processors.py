# -*- coding: utf-8 -*-
# @Author: Pandarison
# @Date:   2018-08-24 15:10:29
# @Last Modified by:   Pandarison
# @Last Modified time: 2018-08-25 21:58:37

import urllib.parse
import os


REGION_CODE = {
    "BR":"br1",
    "EUNE":"eun1",
    "EUW":"euw1",
    "JP":"jp1",
    "KR":"kr",
    "LAN":"la1",
    "LAS":"la2",
    "NA":"na1",
    "OCE":"oc1",
    "TR":"tr1",
    "RU":"ru",
    "PBE":"pbe1"
}

def processor_LeagueFriend(data, region):
    url = "file://" + os.path.realpath('./resources/runes/index.html')
    script = ''
    site = 'Runes'
    return url, script, site



def processor_ProfessorGG(summoners, region):
    url = 'https://porofessor.gg/pregame/{}/'.format(region.lower())
    for player in summoners:
        url = url + "{},".format(urllib.parse.quote(player['internal_name'])) 

    #browser.app
    #$("body").attr("style", "background-color: #FFFFFF"); $(".site-content-bg").attr("style", "background-color: #FFFFFF");
    script = """$("body").attr("style", "background-color: #E3E3E3"); $(".site-content-bg").attr("style", "background-color: #E3E3E3"); $(".site-header").remove();$("#shareinfobanner").remove();$(".site-content-header").remove();$(".site-header-bottom-margin").remove();$("#vmv3-ad-manager").remove(); $(".site-footer").remove(); $("#bigTooltip").remove(); $(".card-5 .cardHeader a").each(
    function(index, element){
"""

    for player in summoners:
        script += "if($(this).html().trim() == \"___SUMMONERNAME___\"){$(this).append(\"<span style='color:rgb(107, 24, 20)'>[___SUMMONERPOSITION___]</span>\");}"
        script = script.replace("___SUMMONERNAME___", player['display_name'])
        script = script.replace("___SUMMONERPOSITION___", player['assigned_role'])
    site = "Professor.GG"
    script += """    }
);"""
    return url, script, site


def processor_OPGG(summoners, region):
    url = 'http://{}.op.gg/multi/query='.format(region.lower())
    for player in summoners:
        url = url + "{}%2C".format(urllib.parse.quote(player['internal_name'])) 

    #$("body").attr("style", "background-color: #FFFFFF"); $(".site-content-bg").attr("style", "background-color: #FFFFFF");
    script = """$("body").attr("style", "background-color: #E3E3E3");
    $(".l-wrap").attr("style", "background-color: #E3E3E3");
    $(".banner_banner--3pjXd").remove();
$("#pnetContVid").remove();
$(".l-header").remove();
$(".l-menu").remove();
$(".PageHeaderWrap").remove();
$(".Header").remove();
$(".life-owner").remove();
$(".l-footer").remove();
$("#hs-beacon").remove();
$("body").attr("style","padding-top:0");"""
    
    site = "OP.GG"
    
    for player in summoners:
        script += "$('.SummonerName').each(function(index, element){if($(this).html() == '___SUMMONERNAME___'){$(this).append(\"<span style='color:rgb(107, 24, 20)'> [___SUMMONERPOSITION___]</span>\");} });"
        script = script.replace("___SUMMONERNAME___", player['display_name'])
        script = script.replace("___SUMMONERPOSITION___", player['assigned_role'])
    return url, script, site


def processor_BlitzPostGame(data, region):
    global REGION_CODE
    url = 'https://app.blitz.gg/lol/match/{}/{}/{}'.format(REGION_CODE[region], urllib.parse.quote(data['playerName']), str(data['gameID']))
    script = """(function() {
    // Load the script
    var script = document.createElement("SCRIPT");
    script.src = 'https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js';
    script.type = 'text/javascript';
    script.onload = function() {
        var $ = window.jQuery;
        $('div').filter(function() {
            var self = $(this);
            return self.height() === 60 &&
                   self.css('flex-direction') === 'row' &&
                   self.css('max-width') === '1440px' &&
                   self.css('display') === 'flex';
        }).remove();
        $('div').filter(function() {
            var self = $(this);
            return self.height() === 38 &&
                   self.css('position') === 'relative' &&
                   self.css('padding-right') === '16px' &&
                   self.css('display') === 'flex';
        }).remove();
    };
    document.getElementsByTagName("head")[0].appendChild(script);
})();"""
    site = "Blitz.GG"
    return url, script, site