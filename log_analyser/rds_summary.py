#!/usr/bin/python

import sys
from log_parser import *

#class Pattern:
#    RPL_INFO = r"[rds_ru_rpl_gen][RDS] Current policy:"

#07-06 15:38:41.567613  3753  3805 I MAL-RDS :  (          rds_ru_rpl_gen, 8330) [RDS-I][RU][rds_ru_rpl_gen][RDS] Current policy: fgimsolte_en<1>, fgwfc_en<1>, erdspolicy<2:2>,||Threshold i4wifirssih<-75>, i4wifirssil<-85>, i4wifirssih_ho<-78>, i4wifirssil_ho<-88>, i4wifisnrh<10>, i4wifisnrl<6>||Threshold i4ltersrph<-106>, i4ltersrpm<-111>, i4ltersrpl<-116>, i4ltersrqh<5>, i4ltersrqm<3>, i4ltersrql<1>||Threshold i43grscph<-85>, i43grscpl<-105>, i42grssih<-83>, i42grssil<-103>, i4lterssnrl<-3>, i43gecnol<-15>||current rds ru status: i4wifirssi<-45>, i4wifisnr<9999>, i4ltersrp<-141>, i4ltersrp_high<-141>, i4ltersrp_low<-141>, i4ltersrq<0>, u4active_ran<1>, i4lterssnr<-50>, i43grscp<-141>, i43gecno<-24>, i42grssi<-141>, u4sig_reg_status<0>||current wifi backhaul : rtp_plr<0>, rtp_jitter<0>, ping_ind<0>, ltecsr_ind<0>, ||pcscf acc stat : volte<1>, wfc<1> || wifi acc_ctrl:<0>, || current MD stat : MD1 roam <0>, ||Call stat : IR92<0>, IR94<0>, SMS over IP<0>, sim<1>

#32737 07-05 12:37:45.766298 14061 14100 I MAL-Daemon:  (rds_rb_setup_data_call_r, 1808) [RDS-I][RDS][rds_rb_setup_data_call_req][RB] get SDC(cnt:1) req, apn<gtnet>, ifid<0>, ims<0>, pro<0>, ran<0>, isEmg<0>, profile<0>

class RdsPatterns(Patterns):
    def __init__(self):
        Patterns.__init__(self)
        # Settings
        self.IMS_ENABLE = self.add(r'.*\[rds_ru_rpl_gen\]\[RDS\] Current policy:.*fgimsolte_en<(\d)>')
        self.WFC_ENABLE = self.add(r'.*\[rds_ru_rpl_gen\]\[RDS\] Current policy:.*fgwfc_en<(\d)>')
        self.PREFERENCE_MODE = self.add(r'.*\[rds_ru_rpl_gen\]\[RDS\] Current policy:.*erdspolicy<(\d)>')
        self.WIFI_RSSI_THRES = self.add(r'.*\[rds_ru_rpl_gen\]\[RDS\] Current policy:.*Threshold i4wifirssih<([-?\d]+)>, i4wifirssil<([-?\d]+)>')
        self.WIFI_RSSI_HANDOVER_THRES = self.add(r'.*\[rds_ru_rpl_gen\]\[RDS\] Current policy:.*i4wifirssih_ho<([-?\d]+)>, i4wifirssil_ho<([-?\d]+)>')
        self.WIFI_SNR_THRES = self.add(r'.*\[rds_ru_rpl_gen\]\[RDS\] Current policy:.*i4wifisnrh<([-?\d]+)>, i4wifisnrl<([-?\d]+)>')
        self.LTE_RSRP_THRS = self.add(r'.*\[rds_ru_rpl_gen\]\[RDS\] Current policy:.*i4ltersrph<([-?\d]+)>, i4ltersrpm<([-?\d]+)>, i4ltersrpl<([-?\d]+)>')
        self.LTE_RSRQ_THRS = self.add(r'.*\[rds_ru_rpl_gen\]\[RDS\] Current policy:.*i4ltersrqh<([-?\d]+)>, i4ltersrqm<([-?\d]+)>, i4ltersrql<([-?\d]+)>')
        self.LTE_RSSNR_THRS = self.add(r'.*\[rds_ru_rpl_gen\]\[RDS\] Current policy:.*i4lterssnrl<([-?\d]+)>')
        self.c3G_RSCP_THRS = self.add(r'.*\[rds_ru_rpl_gen\]\[RDS\] Current policy:.*i43grscph<([-?\d]+)>, i43grscpl<([-?\d]+)>')
        self.c3G_ECNO_THRS = self.add(r'.*\[rds_ru_rpl_gen\]\[RDS\] Current policy:.*i43gecnol<([-?\d]+)>')
        self.c2G_RSSI_THRS = self.add(r'.*\[rds_ru_rpl_gen\]\[RDS\] Current policy:.*i42grssih<([-?\d]+)>, i42grssil<([-?\d]+)>')
        
        # RPLs
        self.WIFI_RSSI = self.add(r'.*\[rds_ru_rpl_gen\]\[RDS\].*i4wifirssi<([-?\d]+)>')
        self.WIFI_SNR = self.add(r'.*\[rds_ru_rpl_gen\]\[RDS\].*i4wifisnr<([-?\d]+)>')
        self.LTE_RSRP = self.add(r'.*\[rds_ru_rpl_gen\]\[RDS\].*i4ltersrp<([-?\d]+)>')
        self.LTE_RSRQ = self.add(r'.*\[rds_ru_rpl_gen\]\[RDS\].*i4ltersrq<([-?\d]+)>')
        self.RTP_PLR = self.add(r'.*\[rds_ru_rpl_gen\]\[RDS\].*rtp_plr<([-?\d]+)>')
        self.RTP_JITTER = self.add(r'.*\[rds_ru_rpl_gen\]\[RDS\].*rtp_jitter<[-?\d]+>')
        self.PING = self.add(r'.*\[rds_ru_rpl_gen\]\[RDS\].*ping_ind<([-?\d]+)>')
        self.CALL_STAT = self.add(r'.*\[rds_ru_rpl_gen\]\[RDS\].*IR92<([-?\d]+)>, IR94<([-?\d]+)>')
        
        # Session
        self.SETUP_DATA_CALL_REQ = self.add(r'.*(?:\[rds_rb_setup_data_call_req\]\[RB\] get SDC|SDC\(cnt:\d+\) req for APN)')
        self.SELECTED_RAT = self.add(r'.*for APN<(.+),0> select on: <(.+)>, cnf2rild')
        self.PDN_REJECT = self.add(r'.*\[rds_rb_setup_data_call_req\] SDC\(cnt:(\d+)\) req for APN<(.+)> not valid: state<0,2>')

class RdsLogAnalyzer:
    def __init__(self, path):
        self._patterns = RdsPatterns()
        self._parser = parser = LogParser(path, self._patterns)
    
    #def analysis(self):

    def sdc_report(self):
        for i in range(20):
            p = self._parser
            sdc_req = p.nth_log_of(self._patterns.SETUP_DATA_CALL_REQ, i)
            ims_switch = p.prev_log_of(self._patterns.IMS_ENABLE, sdc_req)
            wfc_switch = p.prev_log_of(self._patterns.WFC_ENABLE, sdc_req)
            selected_rat = p.nth_log_between(self._patterns.SELECTED_RAT, 1, sdc_req, 
                    p.next_log_of(self._patterns.SETUP_DATA_CALL_REQ, sdc_req))
            print '[%s] receive a setup_data_call request' %(sdc_req.time)
            self.search_ui(sdc_req.time)
            self.search_thrshould(sdc_req.time)
            self.search_rpl(sdc_req.time)
            if selected_rat:
                print '- Selected RAT: %s' %(selected_rat.nth(1) if selected_rat else 'NON FOUND')
            elif p.nth_log_between(self._patterns.PDN_REJECT, 1, sdc_req,
                    p.next_log_of(self._patterns.SETUP_DATA_CALL_REQ, sdc_req)):
                print '- Reject cause: Already activated on Wi-Fi'
            print '\n'

    def search_thrshould(self, time):
        p = self._parser
        wifi_rssi_thres = p.prev_log_before(self._patterns.WIFI_RSSI_THRES, time)
        wifi_rssi_handover_thres = p.prev_log_before(self._patterns.WIFI_RSSI_HANDOVER_THRES, time)
        wifi_snr_thres = p.prev_log_before(self._patterns.WIFI_SNR_THRES, time)
        lte_rsrp_thres = p.prev_log_before(self._patterns.LTE_RSRP_THRS, time)
        lte_rsrq_thres = p.prev_log_before(self._patterns.LTE_RSRQ_THRS, time)
        lte_rssnr_thres = p.prev_log_before(self._patterns.LTE_RSSNR_THRS, time)
        c3g_rscp_thres = p.prev_log_before(self._patterns.c3G_RSCP_THRS, time)
        c3g_ecno_thres = p.prev_log_before(self._patterns.c3G_ECNO_THRS, time)
        c2g_rssi_thres = p.prev_log_before(self._patterns.c2G_RSSI_THRS, time)
        print '- Threshold Settings (%s):' %time
        print '  * Wi-Fi RSSI Threshold: %s' %(str(tuple(wifi_rssi_thres.values)))
        print '  * Wi-Fi RSSI Handover Threshold: %s' %(str(tuple(wifi_rssi_handover_thres.values)))
        print '  * Wi-Fi SNR Threshold: %s' %(str(tuple(wifi_snr_thres.values)))
        print '  * LTE RSRP Threshold: %s' %(str(tuple(lte_rsrp_thres.values)))
        print '  * LTE RSRQ Threshold: %s' %(str(tuple(lte_rsrq_thres.values)))
        print '  * LTE RSSNR Threshold: %s' %(str(tuple(lte_rssnr_thres.values)))
        print '  * 3G RESP Threshold: %s' %(str(tuple(c3g_rscp_thres.values)))
        print '  * 3G ECNO Threshold: %s' %(str(tuple(c3g_ecno_thres.values)))
        print '  * 2G RSSI Threshold: %s' %(str(tuple(c2g_rssi_thres.values)))
    
    def search_rpl(self, time):
        p = self._parser
        wifi_rssi = p.prev_log_before(self._patterns.WIFI_RSSI, time)
        wifi_snr = p.prev_log_before(self._patterns.WIFI_SNR, time)
        lte_rsrp = p.prev_log_before(self._patterns.LTE_RSRP, time)
        lte_rsrq = p.prev_log_before(self._patterns.LTE_RSRQ, time)
        print '- Current RPL (%s):' %time
        print '  * Wi-Fi RSSI: %s' %(wifi_rssi.scalar)
        print '  * Wi-Fi SNR: %s' %(wifi_snr.scalar)
        print '  * LTE RSRP: %s' %(lte_rsrp.scalar)
        print '  * LTE RSRQ: %s' %(lte_rsrq.scalar)

    def search_ui(self, time):
            p = self._parser
            ims_switch = p.prev_log_before(self._patterns.IMS_ENABLE, time)
            wfc_switch = p.prev_log_before(self._patterns.WFC_ENABLE, time)
            print '- UI Settings (%s):' %time
            print '  * IMS Switch: %s' %(self.switch_to_str(ims_switch.scalar))
            print '  * WFC Switch: %s' %(self.switch_to_str(wfc_switch.scalar))
        

    def switch_to_str(self, v):
        return ['DISABLE', 'ENABLED'][int(v) > 0] if v else 'UNKNOWN'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "%s <log path>" %(sys.argv[0])
        exit()
    path = sys.argv[1]
    rds_log_analyzer = RdsLogAnalyzer(path)
    rds_log_analyzer.sdc_report()    
    #rds_log_analyzer.search_ui('12:38:02.766600')    
