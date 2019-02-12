# -*- coding: utf-8 -*-

from odoo import models, fields, api



from datetime import  timedelta
from odoo.addons.tsbd.models.tool import  request_html, get_or_create_object_sosanh
from bs4 import BeautifulSoup
from odoo.exceptions import UserError
import re
import datetime






def thapphan(td):
#     print ('td*** in thappan',td)
    if '/' in td:
        if ' ' in td:
            al = td.split(' ')
            td = float(al[0]) + thapphan(al[1])
        else:
            al = td.split('/')
            td = float(al[0])/float(al[1])
    else:
        try:
            td = float(td)
        except:
            td = False
    return td
def thap_phan_co_2_cham(td):
    td = td.get_text()
    if ':' in td:
        al = td.split(':')
        td = thapphan(al[1]) - thapphan(al[0])
    else:
        td = thapphan(td)
    return td

# 04/02
def get_soup(link):
    html  = request_html(link)
    soup = BeautifulSoup(html, 'html.parser')
    return soup
def get_fix_id(match_link):
        if not match_link:
            return None
        rs = re.search(r'Fix_(\d*?)\.aspx', match_link)
        fix_id = rs.group(1)
        return fix_id
def get_soup_ajax_link(fix_id,template_link):
#     fix_id = get_fix_id(match_link)
    score_link = template_link%fix_id
    html  = request_html(score_link)
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def get_team_date(self, match_link, add_update_dict):
        if any(['home' not in add_update_dict, 'away' not in add_update_dict, ('time' not in add_update_dict and 'date' not in add_update_dict)]):
            if match_link == False:
                raise UserError('not match_link but add_update_dict %s'%add_update_dict)
            soup = get_soup(match_link)
        else:
            pass
        if  'home' not in add_update_dict:
            home = soup.select('div#scr_home a')[0].get_text()
            home = re.sub('\s+\[\d+\]', '', home)
        else:
            home = add_update_dict['home']
        if 'away' not in add_update_dict:
            away = soup.select('div#scr_away a')[0].get_text()
            away = re.sub('\[\d+\]\s+', '', away)
        else:
            away = add_update_dict['away']
        if 'time' not in add_update_dict and  'date' not in add_update_dict:
            begin_time = soup.select('div#scr_start')[0].get_text()
            begin_time = begin_time[9:]
            
            dtime = datetime.datetime.strptime(begin_time,'%d/%m/%Y %H:%M') - timedelta(hours=7)
            str_time = fields.Datetime.to_string(dtime)
            match_date = dtime.date()
            str_date = fields.Date.to_string(match_date)
                
                
        else:
            if 'time' in add_update_dict:
                begin_time = add_update_dict['time']
                dtime = datetime.datetime.strptime(begin_time,'%d/%m/%Y %H:%M') - timedelta(hours=7)
                str_time = fields.Datetime.to_string(dtime)
                match_date = dtime.date()
                str_date = fields.Date.to_string(dtime)
            else:
                match_date = datetime.datetime.strptime(add_update_dict['date'],'%d/%m/%Y')
                str_date = fields.Date.to_string(match_date)
                str_time = None
        team1_id = get_or_create_object_sosanh(self,'tsbd.team',{'name':home})
        team2_id = get_or_create_object_sosanh(self,'tsbd.team',{'name':away})
        team_dict = {'team1': team1_id.id,
                            'team2': team2_id.id,
#                             'time':str_time,
                            'date':str_date,
                            
                    }
        return team_dict, match_date, str_time
    
def get_score(fix_id, soup=None,add_update_dict = {}):
    if 'score1' in add_update_dict and 'score2' in add_update_dict and 'state' in add_update_dict and 'curent_time' in add_update_dict:
        score_dict = {'score1': add_update_dict['score1'],
                  'score2': add_update_dict['score2'],
                  'curent_time': add_update_dict['curent_time'],
                  'state': add_update_dict['state']
                  }
    elif 'state' in add_update_dict and add_update_dict['state']==u'Chưa bắt đầu':
        score_dict = {'state':u'Chưa bắt đầu',
                      'curent_time':False,
                      'score1':0,
                      'score2':0,
            }
    else:
        pass
        if not soup:
            template_link = u'http://bongdaso.com/_MatchScoreTable.aspx?FixtureID=%s'
            soup = get_soup_ajax_link(fix_id,template_link)
        div_scores = soup.select('div.score')
        if  not div_scores:
            div_scores = soup.select('span.sscore')
            span = True
        else:
            span =False
        txt_list_divodds = list(map(lambda td: td.get_text(),div_scores))
        try:
            score1 =  int(txt_list_divodds[0])
            score2 =  int(txt_list_divodds[2])
        except:
            score1,score2 =False,False
        if span == False:
            try:
                fixture_status = soup.select('div.fixture_status')[0].get_text().strip()
            except IndexError:
                fixture_status = False
            try:
                curent_time = int(fixture_status)
                state = u'process'
            except:
                curent_time = False
                state = fixture_status
        else:
            state_soups = soup.select('div div')
            state = state_soups[-1].get_text()
            curent_time = False
        score_dict = {'score1':score1,
                      'score2':score2,
                      'curent_time':curent_time,
                      'state':state
                      }
    print ('***add_update_dict***',add_update_dict)
    return score_dict

def get_odds(fix_id, soup =None):
    if not soup:
        
#         template_link = u'http://bongdaso.com/_OddsInfo.aspx?FixtureID=24481&LeagueID=1&SeasonID=50&Flags=ILTO&HomeClubID=140&AwayClubID=15001&HomePrimaryClubID=140&AwayPrimaryClubID=15001&HomeShortCode=NEW&AwayShortCode=WOV&Home=Newcastle&Away=Wolverhampton'
        template_link = u'http://bongdaso.com/_OddsInfo.aspx?FixtureID=%s&LeagueID=1&SeasonID=50&HomeClubID=14&AwayClubID=15001&HomePrimaryClubID=14&AwayPrimaryClubID=15001&HomeShortCode=NEW&AwayShortCode=WOV&Home=Newcastle&Away=Wolverhampton'
        template_link = u'http://bongdaso.com/_OddsInfo.aspx?FixtureID=%s&LeagueID=1&SeasonID=50&HomeClubID=14&AwayClubID=15001&HomePrimaryClubID=14&AwayPrimaryClubID=15001&HomeShortCode=NEW&AwayShortCode=WOV&Home=Newcastle&Away=Wolverhampton'
        soup = get_soup_ajax_link(fix_id,template_link)
    
    divodds = soup.select('div#ABOdds table  tr:nth-of-type(2) td')
    txt_list_divodds = list(map(lambda td: thap_phan_co_2_cham(td) ,divodds))
    odds_dict = {
    'begin_handicap_money1' : txt_list_divodds[0] -1  if txt_list_divodds[0] else False,
    'begin_handicap_money2' : txt_list_divodds[2] -1 if txt_list_divodds[2] else False,
    'begin_handicap' :  txt_list_divodds[1],
    'begin_ou_money1' :txt_list_divodds[4] -1.0 if txt_list_divodds[4] else False,
    'begin_ou_money2' : txt_list_divodds[5] -1.0 if txt_list_divodds[5] else False,
    'begin_ou' :txt_list_divodds[3],
    }
    
    
    
    trow_soups = soup.select('tr table tr')
    score_odd_lst_strows = []
    print ('len(trow_soups)',len(trow_soups))
    for trow in trow_soups:
        score = trow.select('td')
#             td_odd_down = trow.select('td:nth-of-type(1)')
        if score:
            score = score[0].get_text()
            if ' - ' in score:
                a_score_odds = []
                scores  = score.split(' - ')
                a_score_odds.append(scores)
                td2 = trow.select('td:nth-of-type(2)')
                if td2:
                    td2 = td2[0].get_text()
                    a_score_odds.append(td2)
#                     score +=' ' + td2
                score_odd_lst_strows.append(a_score_odds)
#         txt_trows = u'\n'.join(score_odd_lst_strows)
    
    score_odd_lst_strows
    return odds_dict, score_odd_lst_strows
def get_cate(self,fix_id, cate_ex, match_date, soup = None):
    if not soup:
#         template_link = u'http://bongdaso.com/_OtherMatches.aspx?FixtureID=%s&LeagueID=1&SeasonID=106&CountryRegionID=-1&PlayingDate=02-02-2019&Data=casting'
        template_link = u'http://bongdaso.com/_OtherMatches.aspx?FixtureID=%s&{}&CountryRegionID=-1&PlayingDate={}'.format(cate_ex, match_date.strftime('%d-%m-%Y'))
#         raise UserError(template_link)
#         print ('***template_link',template_link)
        soup = get_soup_ajax_link(fix_id,template_link)
    try:
        name = soup.select('table tr.ls')[0].get_text()
    except:
        name = False
    if name:
        cate_id = get_or_create_object_sosanh(self,'tsbd.cate', {'name':name})
        return {'cate_id': cate_id.id}
    else:
        return {}





def gen_mode_2_dict(self,adict, trow, mode=2, cate_name = False):
    if mode ==2 or mode ==3:
        if mode==2:
            offset = 0
            date_format = '%d/%m/%Y'
            time_key = 'date'
        elif mode ==3:
            offset =1
            date_format = '%d/%m/%y %H:%M'
            time_key = 'time'
        nth_home =3 - offset
        nth_away = 5 - offset
        nth_score = 4 - offset
        nth_match_link = 6 - offset
      
    elif mode ==4:
        date_format = '%d/%m %H:%M'
        time_key = 'time'
        nth_match_link = 6
        
    datem =  trow.select('td:nth-of-type(1)')
    print ('datem',datem)
    if datem:
        datem = datem[0].get_text()
        if datem:
            try:
                print ('date2',datem)
                datem_obj = datetime.datetime.strptime(datem, date_format)
                if mode == 3:
                    datem = datem_obj.strftime('%d/%m/%Y %H:%M')
                elif mode ==4:
                    datems = datem.split(' ')
                    datem = datems[0] + '/' + str(fields.Date.from_string(fields.Date.context_today(self)).year) +' ' + datems[1]
            except Exception as e:
                print ('****error%s'%e)
                return 'continue'
        else:
            return 'continue'
    else:
        return 'continue'
    if datem_obj:
        if mode !=4:
            home =  trow.select('td:nth-of-type(%s) a'%nth_home)
            away =  trow.select('td:nth-of-type(%s) a'%nth_away)
            home = home[0].get_text()
            away = away[0].get_text()
        else:
            home_away =  trow.select('td:nth-of-type(2)')[0].get_text()
            home, away =  home_away.split(' - ')
        
        adict['home']= home
        adict['away']= away
        if mode == 2:
            cate =  trow.select('td:nth-of-type(2) img')
            cate = cate[0]
            cate = cate['title']
        else:
            cate = cate_name
        adict['cate']= cate
        adict[time_key]= datem
        
        match_link =  trow.select('td:nth-of-type(%s) a'%nth_match_link)
        if match_link:
            match_link = match_link[0]['href']
            match_link = 'http://bongdaso.com/' + match_link
        else:
            match_link = False
        adict['match_link']=match_link
        
        if mode !=4:
            score_soup =  trow.select('td:nth-of-type(%s)'%nth_score)[0].get_text()
            if '~' in score_soup:
                score_soup = score_soup.split('~')
            elif '*' in score_soup:
                score_soup = score_soup.split('*')
            elif '-' in score_soup:
                score_soup = score_soup.split('-')
            else:
                raise UserError(u'Sao tỷ số lại không có định dạn -, *,~')
            try:
                adict['score1'] = int(score_soup[0])
                adict['score2'] = int(score_soup[1])
                adict['state']= u'Kết thúc'
                adict['curent_time']= False
            except:
                adict['score1'] = False
                adict['score2'] = False
                adict['state']= u'Chưa bắt đầu'
                adict['curent_time']= False
                
        else:
            adict['state']= u'Chưa bắt đầu'
    else:
        return 'continue'
def all_coming_match(self,soup,mode):
    match_link_list = []
    trows = soup.select('table  tr')
    print ('***mode',mode)
    cate_name = False
    if mode ==3:
        cate_soup = soup.select('div.season_info table tr:nth-of-type(1) td:nth-of-type(2)')
        cate_name = cate_soup[0].get_text()
#         raise UserError(cate_name)
    for trow in trows:
        adict = {}
        
        if mode ==1 or mode ==4:
            class_ = trow.get('class')
            if class_ ==['ls']:
                cate_name = trow.get_text()
                continue
        if mode == 1:
            match_link_td = trow.select('td:nth-of-type(5) a')
            if not match_link_td:
                continue
            href =  'http://bongdaso.com/' + match_link_td[0]['href']
            adict['match_link'] = href
            adict['cate'] = cate_name
            begin_time =  trow.select('td:nth-of-type(1)')[0].get_text()
            begin_times = begin_time.split(' ')
            begin_time = begin_times[0] + '/' + str(fields.Date.from_string(fields.Date.context_today(self)).year) +' ' + begin_times[1]
            adict['time']= begin_time
            begin_time =  trow.select('td:nth-of-type(2)')[0].get_text()
            adict['home']= begin_time
            begin_time =  trow.select('td:nth-of-type(4)')[0].get_text()
            adict['away']= begin_time
#         elif mode ==2:
        else:
            rt = gen_mode_2_dict(self,adict, trow,mode,cate_name)
            if rt =='continue':
                continue
        if 'home' not in adict:
            raise UserError(' not home in adict %s in all_coming_match'%adict)
        match_link_list.append( adict)
    print ('***match_link_list',match_link_list)
    return  match_link_list



def update_score_odds (self, txt_trows,match_id):  
    bet_ScoreLines = []
    for score_odd in txt_trows:
        betscore1 = int(score_odd[0][0])
        betscore2 = int(score_odd[0][1])
        odd = float(score_odd[1])
        bet_score_id = get_or_create_object_sosanh(self,'tsbd.betscore', {'betscore1':betscore1, 'betscore2':betscore2})[0].id
        bet_ScoreLine = get_or_create_object_sosanh(self,'tsbd.betscoreline', {'betscore_id':bet_score_id, 'match_id':match_id}, {'odd':odd})
        bet_ScoreLines.append(bet_ScoreLine)
    return bet_ScoreLines
class Leech(models.Model):
    _name = 'tsbd.leech'
    log = fields.Text()
    log1 = fields.Text()
    parse_log = fields.Text()
    link = fields.Char()
    all_match_link = fields.Char()
    match_ids = fields.Many2many('tsbd.match')
    count = fields.Integer()
    is_get_thong_ke = fields.Boolean()
    all_match_link_select= fields.Selection([('http://bongdaso.com/_PlayedMatches.aspx?LeagueID=-1&SeasonID=-1&Period=1','http://bongdaso.com/_PlayedMatches.aspx?LeagueID=-1&SeasonID=-1&Period=1'),
                                                                ('http://bongdaso.com/Everton-Leicester_City-2019_01_01-_Fix_55956.aspx.aspx?LeagueID=1&SeasonID=106&Data=stat','http://bongdaso.com/Everton-Leicester_City-2019_01_01-_Fix_55956.aspx.aspx?LeagueID=1&SeasonID=106&Data=stat mode 2'),
                                                                ('http://bongdaso.com/_ComingMatches.aspx?LeagueID=-1&SeasonID=-1&Period=1&Odd=1','http://bongdaso.com/_ComingMatches.aspx?LeagueID=-1&SeasonID=-1&Period=1&Odd=1'),
                                                                ('http://bongdaso.com/LeagueSchedule.aspx?LeagueID=1&SeasonID=106&CountryRegionID=-1&Period=6',u'Ngoại hạng anh tháng 2'),
                                                                ('http://bongdaso.com/LeagueSchedule.aspx?LeagueID=3&SeasonID=111&CountryRegionID=-1&Period=5',u'Seria tháng 1'),
                                                                ('http://bongdaso.com/LeagueSchedule.aspx?LeagueID=4&SeasonID=110&CountryRegionID=-1&Period=5',u'Laliga tháng 1'),
                                                                ('http://bongdaso.com/LeagueSchedule.aspx?LeagueID=5&SeasonID=109&CountryRegionID=-1&Period=5',u'Đức tháng 1'),
                                                                ('http://bongdaso.com/LeagueSchedule.aspx?LeagueID=6&SeasonID=108&CountryRegionID=-1&Period=5',u'Pháp tháng 1'),
                                             
                                             
                                             ])
    cate_id = fields.Many2one('tsbd.cate')
    bxh_ids = fields.Many2many('tsbd.bxh','leech_bxh_rel','leech_id', 'bxh_id')
    @api.onchange('all_match_link_select')
    def all_match_link_select_oc_(self):
        self.all_match_link = self.all_match_link_select
    @api.multi
    def clean_match(self):
        for r in self.match_ids :
            r.unlink()
            
    @api.multi
    def leech_all_season(self):
        link = self.all_match_link
        for ss in range (0,7):
            aml = re.sub('Period=\d+','Period=%s'%ss,link)
            self.leech_all_match_function(aml, is_get_thong_ke  =  False)
            
    @api.multi
    def bxh(self):
        nha_khach_hoa_rt = []
       
        rt_home_goal = {}
        rs = self.env['tsbd.match'].read_group([('cate_id','=', 38),('state','!=', u'Chưa bắt đầu')],['team1','score1', 'score2'],['team1'], lazy=False)
        for ateam in rs:
            ateams = {}
            ateams['home_match_number'] = ateam['__count']
            ateams['team'] = ateam['team1']
            ateams['score1'] = ateam['score1']
            ateams['score2'] = ateam['score2']
            rt_home_goal[ateam['team1'][0]] = ateams
            
        
        rt_away_goal = {}
        rs = self.env['tsbd.match'].read_group([('cate_id','=', 38),('state','!=', u'Chưa bắt đầu')],['team2','score1', 'score2'],['team2'], lazy=False)
        for ateam in rs:
            ateams = {}
            ateams['away_match_number'] = ateam['__count']
            ateams['team'] = ateam['team2']
            ateams['score1'] = ateam['score1']
            ateams['score2'] = ateam['score2']
            rt_away_goal[ateam['team2'][0]] = ateams
            
            
            
        
        rt_home_win= {}
        rs = self.env['tsbd.match'].read_group([('cate_id','=', 38),('state','!=', u'Chưa bắt đầu')],['team1','winner','score1', 'score2'],['team1', 'winner'], lazy=False)
        for ateam in rs:
            if ateam['team1'] == ateam['winner']:
                ateams = {}
                ateams['team'] = ateam['team1']
                ateams['home_win_count'] = ateam['__count']
                ateams['score1'] = ateam['score1']
                ateams['score2'] = ateam['score2']
                rt_home_win[ateam['team1'][0]] = ateams
        nha_khach_hoa_rt.append(rt_home_win)  
        
        
        rt_away_win= {}
        rs = self.env['tsbd.match'].read_group([('cate_id','=', 38),('state','!=', u'Chưa bắt đầu')],['team2','winner','score1', 'score2'],['team2', 'winner'], lazy=False)
        for ateam in rs:
            if ateam['team2'] == ateam['winner']:
                ateams = {}
                ateams['team'] = ateam['team2']
                ateams['away_win_count'] = ateam['__count']
                ateams['score1'] = ateam['score1']
                ateams['score2'] = ateam['score2']
                rt_away_win[ateam['team2'][0]] = ateams
        nha_khach_hoa_rt.append(rt_away_win)  
        
        
        
        
        #san nhà
        rt_home_draw = {}
        rs = self.env['tsbd.match'].read_group([('cate_id','=', 38),('state','!=', u'Chưa bắt đầu'),('winner','=', False),('loser','=', False)],['team1','score1', 'score2'],['team1'], lazy=False)
        for ateam in rs:
            ateams = {}
            ateams['team'] = ateam['team1']
            ateams['home_draw_count'] = ateam['__count']
            ateams['score1'] = ateam['score1']
            ateams['score2'] = ateam['score2']
            rt_home_draw[ateam['team1'][0]] = ateams
        nha_khach_hoa_rt.append(ateams)  
        
        #san khach
        rt_away_draw = {}
        rs = self.env['tsbd.match'].read_group([('cate_id','=', 38),('state','!=', u'Chưa bắt đầu'),('winner','=', False),('loser','=', False)],['team2','score1', 'score2'],['team2'], lazy=False)
        
        for ateam in rs:
            ateams = {}
            ateams['team'] = ateam['team2']
            ateams['away_draw_count'] = ateam['__count']
            ateams['score1'] = ateam['score1']
            ateams['score2'] = ateam['score2']
            
            rt_away_draw[ateam['team2'][0]] = ateams
        
        nha_khach_hoa_rt.append(rt_away_draw)  
        rs = {}
        
        sum_teams = {}
        bxh_ids = []
        for team,ateam  in rt_home_win.items():
            new_ateam = {}
#             new_ateam['team'] = team
            new_ateam['home_t'] = ateam['home_win_count']
            new_ateam['away_t'] = rt_away_win.get(team, {}).get('away_win_count',0)
           
            new_ateam['home_h'] = rt_home_draw.get(team, {}).get('home_draw_count',0)
            new_ateam['away_h'] = rt_away_draw.get(team, {}).get('away_draw_count',0)
            
            new_ateam['home_tg'] = rt_home_goal.get(team, {}).get('score1',0)
            new_ateam['home_th'] = rt_home_goal.get(team, {}).get('score2',0)
            new_ateam['home_match_number'] = rt_home_goal.get(team, {}).get('home_match_number',0)

            new_ateam['away_tg'] = rt_away_goal.get(team, {}).get('score2',0)
            new_ateam['away_th'] = rt_away_goal.get(team, {}).get('score1',0)
            new_ateam['away_match_number'] = rt_away_goal.get(team, {}).get('away_match_number',0)
            
            bxh_id = get_or_create_object_sosanh(self,'tsbd.bxh', {'team_id':team}, new_ateam,is_must_update = True)
            bxh_ids.append(bxh_id.id)
            sum_teams[team] = new_ateam
            
        self.bxh_ids = [(6,0,bxh_ids)]
#         leech_ids
        bxh_ids = self.env['tsbd.bxh'].search([('leech_ids.id','=',self.id)])
        for stt,r in enumerate(bxh_ids) :
            r.stt = stt +1
        self.log = ''
        self.log1 = u'%s - %s - %s - %s'%(len(rt_home_win), len(rt_away_win), len(rt_home_draw), len(rt_away_draw))
    @api.multi
    def trig(self):
        matchs= self.env['tsbd.match'].search([])
        matchs.write({'trig':True})
#         self.match_ids = [(5,0)]
    def get_update_dict(self,match_link,match_date, is_get_thong_ke = True,add_update_dict = {},str_time=None):
        
        fix_id = get_fix_id(match_link)
        
        update_dict = {}
        score_and_status_dict = get_score(fix_id, add_update_dict=add_update_dict)
        update_dict.update(score_and_status_dict)
        score_odd_lst_strows = []
        if match_link:
            odds_adict, score_odd_lst_strows = get_odds(fix_id)
            update_dict.update(odds_adict)
       
        
#         cate = add_update_dict['cate']
        if 'cate'  in add_update_dict :
            update_dict['cate_id']  = get_or_create_object_sosanh(self,'tsbd.cate', {'name':add_update_dict['cate']}).id
        else:
            if match_link:
                cate_ex = re.search(r'\?(.*$)',match_link).group(1)
                cate_dict = get_cate(self, fix_id,cate_ex, match_date)
                update_dict.update(cate_dict )
        
        update_dict['match_link']  = match_link or add_update_dict.get('match_link')
        if str_time:
            update_dict['time'] = str_time
        if is_get_thong_ke and match_link:
            match_link  = re.sub('&Data=(.*?)$','',match_link)
            statictis_link =match_link +'&Data=stat'
            print ('***statictis_link',statictis_link)
#             raise UserError(statictis_link)
            statictis_match_ids = self.leech_all_match_function(statictis_link, is_write = False, break_count=6, is_get_thong_ke  = False, take_match_not_link=False)
            statictis_match_dict = {'statictis_match_ids':[(6,0,statictis_match_ids)]}
            update_dict.update(statictis_match_dict)
#         print ('***update_dict',update_dict)
        return update_dict, score_odd_lst_strows
    
    def leeching_a_match_function(self,match_link, is_write = True, is_get_thong_ke  = True,add_update_dict = {}):
#         search_dict = {}
#         search_list_fields = []
        team_and_begintime,match_date, str_time = get_team_date(self,match_link,add_update_dict)
        search_dict =team_and_begintime
#         if is_write == False:
#             match_id = get_or_create_object_sosanh(self,'tsbd.match', search_dict, is_create=False, is_write =False)
#             if not match_id:
#                 update_dict, txt_trows = self.get_update_dict (match_link,match_date, is_get_thong_ke =  is_get_thong_ke, add_update_dict = add_update_dict,str_time=str_time)
# #                 raise UserError(u'%s'%search_dict)
#                 match_id = get_or_create_object_sosanh(self,'tsbd.match', search_dict, update_dict )
#         else:
        update_dict, txt_trows = self.get_update_dict (match_link,match_date, is_get_thong_ke =  is_get_thong_ke, add_update_dict=add_update_dict,str_time = str_time )
        match_id = get_or_create_object_sosanh(self,'tsbd.match', search_dict, update_dict)
       
        bet_ScoreLines = update_score_odds(self, txt_trows,match_id.id)
        self.log = bet_ScoreLines
        return match_id.id
    
    def leech_a_match(self):
        match_id = self.leeching_a_match_function(self.link)
        self.match_ids = [(4,match_id)]
    def leech_all_match_function(self, all_match_link, break_count=0, is_write=True,is_get_thong_ke = True, take_match_not_link = True):
        soup = get_soup(all_match_link)
        if '_PlayedMatches' in all_match_link:
            #http://bongdaso.com/_PlayedMatches.aspx?LeagueID=-1&SeasonID=-1&Period=1
            mode = 1
        elif 'Data=stat' in all_match_link:
            #http://bongdaso.com/Everton-Leicester_City-2019_01_01-_Fix_55956.aspx.aspx?LeagueID=1&SeasonID=106&Data=stat
            mode = 2
        elif '_ComingMatches' in all_match_link:
        #http://bongdaso.com/_ComingMatches.aspx?LeagueID=-1&SeasonID=-1&Period=1&Odd=1
            mode = 4
        else:
            #http://bongdaso.com/LeagueSchedule.aspx?LeagueID=1&SeasonID=106&CountryRegionID=-1&Period=5
            mode = 3
#         raise UserError(mode)
        match_link_list = all_coming_match(self,soup,mode)
#         print ('***match_link_list',match_link_list)
        count = 0 
        len_match_ids = len(match_link_list)
        m_ids = []
        for adict in match_link_list:
            add_update_dict = adict#{'cate': adict['cate']}
            print ('***adict ', adict)
            match_link = adict['match_link']
            if not take_match_not_link and  not match_link:
                continue
            m_id = self.leeching_a_match_function(match_link,is_write = is_write, is_get_thong_ke= is_get_thong_ke, add_update_dict=add_update_dict)
            m_ids.append(m_id)
            print ('%s/%s,%s'%(count, len_match_ids, add_update_dict))
            count+=1
            if break_count and break_count == count:
                break
        return m_ids
    def leech_all_match(self):
        m_ids = self.with_context({'leech_all_match_function':True}).leech_all_match_function( self.all_match_link, self.count, is_get_thong_ke = self.is_get_thong_ke )
        for m_id in m_ids:
            self.write( {'match_ids': [(4,m_id)]})
            
    def test(self):
        template_link = u'http://bongdaso.com/_OddsInfo.aspx?FixtureID=%s&LeagueID=1&SeasonID=50&HomeClubID=14&AwayClubID=15001&HomePrimaryClubID=14&AwayPrimaryClubID=15001&HomeShortCode=NEW&AwayShortCode=WOV&Home=Newcastle&Away=Wolverhampton'
        fix_id = get_fix_id(self.link)
        soup = get_soup_ajax_link(fix_id,template_link)
#         trow_soups = soup.select('div#WHScoreOdd tr')
#         trow_soups = soup.select('div#WHScoreOdd tr')
        trow_soups = soup.select('tr table tr')
        score_odd_lst_strows = []
        print ('len(trow_soups)',len(trow_soups))
        for trow in trow_soups:
            score = trow.select('td')
#             td_odd_down = trow.select('td:nth-of-type(1)')
            if score:
                score = score[0].get_text()
                if ' - ' in score:
                    scores  = score.split(' - ')
                    td2 = trow.select('td:nth-of-type(2)')
                    if td2:
                        td2 = td2[0].get_text()
                        score +=' ' + td2
                    score_odd_lst_strows.append(score)
        txt_trows = u'\n'.join(score_odd_lst_strows)
        self.log = txt_trows
#         fix_id = get_fix_id(self.link)
#         score_and_status_dict = get_score(fix_id)
        
