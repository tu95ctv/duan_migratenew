# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.addons.tsbd.models.tool import  request_html
# from odoo.addons.tsbd.models.leech import  detail_match
from odoo.addons.tsbd.models.tool import   get_or_create_object_sosanh

from bs4 import BeautifulSoup

from odoo.addons.tsbd.models.bet import handicap_winning_ 

# import re
# from odoo.osv import expression


class Team(models.Model):
    _name='tsbd.team'
    name = fields.Char()
    
    @api.multi
    def name_get(self):
        rs = []
        for r in self:
            
            stt = self.env['tsbd.bxh'].search([('team_id','=',r.id)])
            if stt:
                stt = stt[0].stt
                name_show = u'%s(%s)'%(r.name,stt)
            else:
                name_show = r.name
            rs.append((r.id,name_show))
        return rs
    
    
    
 
class Cate(models.Model):  
    _name = 'tsbd.cate' 
    name = fields.Char()
    match_ids = fields.One2many('tsbd.match', 'cate_id')
    cate_ids = fields.One2many('tsbd.bxh','cate_id')
    @api.multi
    def trig(self):
        matchs= self.env['tsbd.match'].search([])
        matchs.write({'trig':True})
    @api.multi
    def bxh(self):
        nha_khach_hoa_rt = []
       
        rt_home_goal = {}
        rs = self.env['tsbd.match'].read_group([(('cate_id','=', self.id)),('state','!=', u'Chưa bắt đầu')],['team1','score1', 'score2'],['team1'], lazy=False)
        for ateam in rs:
            ateams = {}
            ateams['home_match_number'] = ateam['__count']
            ateams['team'] = ateam['team1']
            ateams['score1'] = ateam['score1']
            ateams['score2'] = ateam['score2']
            rt_home_goal[ateam['team1'][0]] = ateams
            
        
        rt_away_goal = {}
        rs = self.env['tsbd.match'].read_group([(('cate_id','=', self.id)),('state','!=', u'Chưa bắt đầu')],['team2','score1', 'score2'],['team2'], lazy=False)
        for ateam in rs:
            ateams = {}
            ateams['away_match_number'] = ateam['__count']
            ateams['team'] = ateam['team2']
            ateams['score1'] = ateam['score1']
            ateams['score2'] = ateam['score2']
            rt_away_goal[ateam['team2'][0]] = ateams
            
            
            
        
        rt_home_win= {}
        rs = self.env['tsbd.match'].read_group([(('cate_id','=', self.id)),('state','!=', u'Chưa bắt đầu')],['team1','winner','score1', 'score2'],['team1', 'winner'], lazy=False)
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
        rs = self.env['tsbd.match'].read_group([(('cate_id','=', self.id)),('state','!=', u'Chưa bắt đầu')],['team2','winner','score1', 'score2'],['team2', 'winner'], lazy=False)
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
        rs = self.env['tsbd.match'].read_group([(('cate_id','=', self.id)),('state','!=', u'Chưa bắt đầu'),('winner','=', False),('loser','=', False)],['team1','score1', 'score2'],['team1'], lazy=False)
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
        rs = self.env['tsbd.match'].read_group([(('cate_id','=', self.id)),('state','!=', u'Chưa bắt đầu'),('winner','=', False),('loser','=', False)],['team2','score1', 'score2'],['team2'], lazy=False)
        
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
            new_ateam['cate_id'] = self.id
            
            bxh_id = get_or_create_object_sosanh(self,'tsbd.bxh', {'team_id':team}, new_ateam,is_must_update = True)
            bxh_ids.append(bxh_id.id)
            sum_teams[team] = new_ateam
            
#         self.bxh_ids = [(6,0,bxh_ids)]
#         leech_ids
        bxh_ids = self.env['tsbd.bxh'].search([('cate_id','=',self.id)])
        for stt,r in enumerate(bxh_ids) :
            r.stt = stt +1
#         self.log = ''
#         self.log1 = u'%s - %s - %s - %s'%(len(rt_home_win), len(rt_away_win), len(rt_home_draw), len(rt_away_draw))
        
        
class BetScore(models.Model):
    _name ='tsbd.betscore'
    betscore1 = fields.Integer()
    betscore2 = fields.Integer()
    @api.multi
    def name_get(self):
        rs = []
        for r in self:
            name_show = u'%s-%s'%(r.betscore1, r.betscore2)
            rs.append((r.id,name_show))
        return rs
            
        
class BetScoreLine(models.Model):
    _name ='tsbd.betscoreline'
    betscore_id = fields.Many2one('tsbd.betscore')
    match_id = fields.Many2one('tsbd.match')
    odd = fields.Float()
    
    @api.constrains('betscore_id','match_id','odd')
    def scoreline(self):
        for r in self:
            if (r.match_id.score1 == r.betscore_id.betscore1) and  (r.match_id.score2 == r.betscore_id.betscore2):
                r.match_id.score_odd = r.odd
def adecorator(func):
    def awrapper(*arg,**karg):  
        self = arg[0]
        for r in self:
            if r.state != u'Chưa bắt đầu':
                func(r)
    return awrapper
        
sign = lambda x: (-1, 1)[x > 0]
      
class Match(models.Model):
    _name = 'tsbd.match'
    _order = 'date desc'
    @api.multi    
    def detail_match_button(self):
        pass
#         search_dict,update_dict = detail_match(self, self.link)
#         search_dict.update(update_dict)
#         self.write(search_dict)
        
    def get_odds_button(self):
        rs= self.get_odds(self.link)
        raise UserError(u'%s'%rs)


    @api.multi
    def leech_button(self):
        rs  = request_html(self.link)
        file = open('/media/sf_C_DRIVE/D4/dl/testfile.html','w') 
        file.write(rs) 
        file.close() 
        self.log =rs
        
    @api.multi
    def parse_button(self):
        pass
#         file = open('/media/sf_C_DRIVE/D4/dl/testfile.html','r') 
#         html = file.read()
#         soup = BeautifulSoup(html, 'html.parser')
#         txt_trows = all_coming_match(soup)
#         self.parse_log =txt_trows
        
        
    log = fields.Text()
    parse_log = fields.Text()
    link = fields.Char()
    betscoreline_ids = fields.One2many('tsbd.betscoreline', 'match_id')
    def default_time(self):
        if 'leech_all_match_function' in self._context:
            return False
        else:
            return fields.Datetime.now()
    time= fields.Datetime(default= default_time)
    date = fields.Date()
    
    current_time =  fields.Float()
    state = fields.Char()
    cate_id = fields.Many2one('tsbd.cate')
    name = fields.Char(compute='name_',store=True)
    @api.depends('team1','team2','time','score1','score2')
    def name_(self):
        for r in self:
            try:
                time_txt = fields.Datetime.from_string(r.time).strftime('%d/%m/%Y %H:%M')
                name = r.team1.name + '    ' + str(r.score1) +' - ' + str(r.score2) + '    ' + r.team2.name + '    ' + time_txt
                r.name = name
            except:
                pass
    match_link = fields.Char()
    score_odd = fields.Float()
    team1= fields.Many2one('tsbd.team')
    team2= fields.Many2one('tsbd.team')
    score1 = fields.Integer(default=False)
    score2 = fields.Integer()
    event_ids =  fields.One2many('tsbd.event','match_id')
    bet_ids =  fields.One2many('tsbd.bet','match_id')
    
    begin_handicap_money1 =  fields.Float(default=100,digit=(6,3))
    begin_handicap_money2 =  fields.Float(default=100,digit=(6,3))
    begin_handicap =  fields.Float(digit=(6,2))
    
    begin_ou_money1 =  fields.Float(default=100,digit=(6,3))
    begin_ou_money2 =  fields.Float(default=100,digit=(6,3))
    begin_ou =  fields.Float(digit=(6,2))
    
    curent_handicap_money1 =  fields.Float(default=100,digit=(6,3))
    curent_handicap_money2 =  fields.Float(default=100,digit=(6,3))
    curent_handicap = fields.Float(digit=(6,2))
    
    curent_ou_money1 =  fields.Float(default=100,digit=(6,3))
    curent_ou_money2 =  fields.Float(default=100,digit=(6,3))
    curent_ou =  fields.Float(digit=(6,2))
    
    predict_ids = fields.One2many('tsbd.predict','match_id')
    total_winning_amount = fields.Float(compute='total_winning_amount_',store=True)
    link = fields.Char()
    
    handicap_winner = fields.Selection([(u'cua_tren',u'Cửa trên'), (u'cua_duoi',u'Cửa dưới'), (u'hoa_tien',u'Hòa tiền'), (u'team1',u'team1'), (u'team2',u'team2')], compute='_handicap_winner', store=True)
    trig = fields.Boolean()
#     keo_chap_thang_thua = fields.Selection([(u'1_2',u'nửa kèo'), (u'toan_keo', u'Ăn thua'), (u'co_the_hoa',u'Có thể hòa tiền')], compute='_keo_chap_thang_thua', store=True)
    keo_chap_thang_thua = fields.Float(compute='_keo_chap_thang_thua', store=True)
   
    bet_winner = fields.Many2one('tsbd.team', compute='_handicap_winner', store= True)
    bet_loser = fields.Many2one('tsbd.team', compute='_handicap_winner', store= True)
    
    
    winner = fields.Many2one('tsbd.team', compute='_match_winner', store= True)
    loser = fields.Many2one('tsbd.team', compute='_match_winner', store= True)
    over_or_under = fields.Selection([('over','Over'), ('under','Under')], compute='over_or_under_', store=True)
    ou_win_lost = fields.Float(compute='over_or_under_', store=True)
    ou_win_lost_amount = fields.Float(compute='over_or_under_', store=True)
    @api.depends('score1','score2','begin_ou','trig')
    @adecorator
    def over_or_under_(self):
        for r in self:
            ratio, amount = handicap_winning_(None, bet_kind='over',mode='predict', match_id =r, skip_tinh_tien=False)
            if ratio > 0:
                r.over_or_under = 'over'
            elif ratio < 0:
                r.over_or_under = 'under'
                ratio2, amount = handicap_winning_(None, bet_kind='under',mode='predict', match_id =r, skip_tinh_tien=False)
            r.ou_win_lost = ratio
            r.ou_win_lost_amount = amount
    team1_over = fields.Integer(compute = 'team1_over_under_')
    team1_under = fields.Integer(compute = 'team1_over_under_')
    
    team2_over = fields.Integer(compute = 'team1_over_under_')
    team2_under = fields.Integer(compute = 'team1_over_under_')
    
    
    @api.depends('team1_match_ids','trig')
    def team1_over_under_(self):
        for r in self:
            teams =[('team1',r.team1.id), ('team2',r.team2.id)]
            for team_name, team in teams:
                rs1 = self.env['tsbd.match'].read_group(['|', ('team1', '=', team ), ('team2', '=', team )],['over_or_under'], ['over_or_under'], lazy=False )
                for adict in rs1:
                    over_or_under = adict['over_or_under']
                    if over_or_under =='over' or over_or_under =='under':
                        setattr(r, '%s_%s'%(team_name,over_or_under), adict['__count'])
                   
                
    win_lost = fields.Float(compute='win_lost_')
    @api.depends('keo_chap_thang_thua','bet_winner')
    def win_lost_(self):
        team = self._context.get('team')
        if team:
            for r in self:
                bet_winner_id  = r.bet_winner.id 
                if r.bet_winner:
                    if bet_winner_id == team:
                        r.win_lost = r.handicap_win_lost
                    else:
                        r.win_lost = -r.handicap_win_lost
                        
                        
    team1_match_ids = fields.Many2many('tsbd.match', 'match_match_rel', 'match_id', 'team1_match_id', compute='team1_match_ids_')
    team_match_limit = fields.Integer()
    @api.depends('team1','team_match_limit')
    def team1_match_ids_(self):
        for r in self:
            rs = self.env['tsbd.match'].search(['|', ('team1', '=', r.team1.id ), ('team2', '=', r.team1.id ),('state','!=',u'Chưa bắt đầu')],limit=r.team_match_limit or None)
            r.team1_match_ids = [(6,0,rs.ids)]
            
    team2_match_ids = fields.Many2many('tsbd.match', 'match_matchofteam2_rel', 'match_id', 'team2_match_id', compute='team2_match_ids_', )
    @api.depends('team2', 'team_match_limit')
    def team2_match_ids_(self):
        for r in self:
            rs = self.env['tsbd.match'].search(['|', ('team1', '=', r.team2.id ), ('team2', '=', r.team2.id ),('state','!=',u'Chưa bắt đầu')],limit=r.team_match_limit or None)
            r.team2_match_ids = [(6,0,rs.ids)]
            
    sum_handicap_win_lost1 = fields.Float(compute='sum_handicap_win_lost1_', store=True)
    
    @api.depends('team1', 'team2','team_match_limit')
    def sum_handicap_win_lost1_(self):
        print ('đã vô sum_handicap_win_lost1_')
        for r in self:
            limit = r.team_match_limit or None
            team =r.team1.id
            rs1 = self.env['tsbd.match'].read_group([('team1', '=', team )],['team1','handicap_win_lost1'], ['team1'],limit= limit,lazy=True )
            rs2 = self.env['tsbd.match'].read_group([('team2', '=', team )],['team2','handicap_win_lost2'], ['team2'] , limit=limit, lazy=True)
            try:
                r.sum_handicap_win_lost1 = rs1[0]['handicap_win_lost1'] + rs2[0]['handicap_win_lost2']
            except:
                pass
    sum_handicap_win_lost2 = fields.Float(compute='sum_handicap_win_lost2_', store=True)
    @api.depends('team1', 'team2','team_match_limit')
    def sum_handicap_win_lost2_(self):
        for r in self:
            team =r.team2.id
            rs1 = self.env['tsbd.match'].read_group([('team1', '=', team )],['team1','handicap_win_lost1'], ['team1'], limit=r.team_match_limit or None,lazy=False )
            rs2 = self.env['tsbd.match'].read_group([('team2', '=', team )],['team2','handicap_win_lost2'], ['team2'] ,limit=r.team_match_limit or None, lazy=False)
            try:
                r.sum_handicap_win_lost2 = rs1[0]['handicap_win_lost1'] + rs2[0]['handicap_win_lost2']
            except:
                pass
            
            
        
    
        

#     str_win_lost1 = fields.Char(compute='str_win_lost1_')
#     @api.depends('team1_match_ids')
#     def str_win_lost1_(self):
#         for r in self:
#             alist = []
#             for m in  r.with_context(team=r.team1.id).team1_match_ids:
#                 alist.append(m.win_lost)
#             r.str_win_lost1 = alist
    
#     str_win_lost2 = fields.Char(compute='str_win_lost2_')
#     @api.depends('team2_match_ids')
#     def str_win_lost2_(self):
#         for r in self:
#             alist = []
#             for m in  r.with_context(team=r.team2.id).team2_match_ids:
#                 alist.append(m.win_lost)
#             r.str_win_lost2 = alist
#             
#             
            
    handicap_win_lost = fields.Float(compute='handicap_win_lost_', store=True)
    handicap_win_lost1 = fields.Float(compute='handicap_win_lost_', store=True)
    handicap_win_lost2 = fields.Float(compute='handicap_win_lost_', store=True)
    
    @api.depends('score1','score2','begin_handicap', 'trig')
    @adecorator
    def handicap_win_lost_(self):
        for r in self:
            winning_difference = (r.score1 - r.score2 - r.begin_handicap)
            winning_difference_abs = abs(winning_difference)
            if winning_difference_abs ==0.25:
                winning_difference_abs = 0.5
            elif winning_difference_abs ==0:
                winning_difference_abs =0
            else:
                winning_difference_abs =1
            dau = sign(winning_difference)
            r.handicap_win_lost = winning_difference_abs
            
            r.handicap_win_lost1 = dau*winning_difference_abs
            r.handicap_win_lost2 = -dau*winning_difference_abs
        
   
    
                        
   
   
    
    
                
            
    
   
    
    @api.depends('score1','score2','trig')
#     @adecorator
    def _match_winner(self):
        for r in self:
            if r.score1 > r.score2:
                r.winner = r.team1
                r.loser = r.team2
            elif r.score1< r.score2:
                r.winner = r.team2
                r.loser = r.team1         
        
        
    @api.depends('score1', 'score2', 'begin_handicap','state','trig')
    
    def _keo_chap_thang_thua(self):
        for r in self:
            keo_chap_thang_thua = abs(r.begin_handicap - float(int(r.begin_handicap)))
            if keo_chap_thang_thua ==0.75:
                keo_chap_thang_thua = 0.25
#             if keo_chap_thang_thua
            print ('keo_chap_thang_thua',keo_chap_thang_thua)
            r.keo_chap_thang_thua = keo_chap_thang_thua
        
    @api.depends('score1', 'score2', 'begin_handicap','state', 'trig')
    def _handicap_winner(self):
        for r in self:
            if r.state != u'Chưa bắt đầu':
                diff = (r.score1 - r.score2 - r.begin_handicap)
                if diff > 0:
                    doi_thang = 'team1'
                    r.bet_winner = r.team1
                    r.bet_loser = r.team2
                elif diff < 0:
                    doi_thang = 'team2'
                    r.bet_winner = r.team2
                    r.bet_loser = r.team1
                else:
                    doi_thang= 'hoa_tien'
                adict  ={}
                if r.begin_handicap > 0:
                    adict = {'team1':'cua_tren', 'team2':'cua_duoi'}
                elif r.begin_handicap < 0:
                    adict = {'team2':'cua_tren', 'team1':'cua_duoi'}
       
                rs = adict.get(doi_thang, doi_thang)
                r.handicap_winner = rs           
                
                
                
    
    
    @api.depends('bet_ids')
    def total_winning_amount_(self):
        for r in self:
            r.total_winning_amount = sum(r.bet_ids.mapped('winning_amount'))
    
    is_copy_begin_to_curent = fields.Boolean()
    statictis_match_ids =  fields.Many2many('tsbd.match','match_statictis_match_rel','match_id', 'statictis_match_id')
    
    @api.onchange('current_time')
    def _oc_current_time(self):
        current_time = self.current_time
        current_time = current_time + 15 if current_time > 47 else current_time
        self.time = datetime.now() -  timedelta(minutes=current_time)
        
        
    @api.onchange('is_copy_begin_to_curent')
    def _oc_is_copy_begin_to_curent(self):
        if self.is_copy_begin_to_curent:
            for handicap_or_ou in ['handicap','ou']:
                for field in ['_money1','_money2','']:
                    field_name_get = 'begin_' + handicap_or_ou + field
                    field_name_set = 'curent_' + handicap_or_ou + field
                    setattr(self, field_name_set, getattr(self, field_name_get))
            
    
    @api.onchange('event_ids')
    def _oc_event_ids(self):
        if self.event_ids:
            self.score1=self.event_ids[-1].score1
            self.score2=self.event_ids[-1].score2