# link cleaner

settings → tele → privacy → links. opened links, and links in the messages and captions you send, lose these parameters. t.me, telegram.me and telegram.dog links are never touched. hosts are matched case-insensitively.

on every site: `utm*`, `mtm_*`, `pk_campaign`, `pk_kwd`, `pk_keyword`, `pk_source`, `pk_medium`, `pk_content`, `pk_cid`, `ga_*`, `_ga`, `_gl`, `gclid`, `gclsrc`, `gbraid`, `wbraid`, `dclid`, `gad_source`, `gad_campaignid`, `fbclid`, `fb_action_ids`, `fb_action_types`, `fb_source`, `fb_ref`, `action_object_map`, `action_type_map`, `action_ref_map`, `msclkid`, `twclid`, `ttclid`, `li_fat_id`, `epik`, `yclid`, `ysclid`, `_openstat`, `mc_cid`, `mc_eid`, `mc_tc`, `ml_subscriber*`, `mkt_tok`, `igshid`, `igsh`, `_hsenc`, `_hsmi`, `__hsfp`, `__hssc`, `__hstc`, `hsctatracking`, `srsltid`, `s_kwcid`, `s_cid`, `oly_anon_id`, `oly_enc_id`, `rb_clickid`, `vero_conv`, `vero_id`, `wickedid`, `_kx`, `wt_?z?mc`, `wtrid`, `hmb_campaign`, `hmb_medium`, `hmb_source`, `itm_campaign`, `itm_medium`, `itm_source`, `otm_*`, `cmpid`, `os_ehash`, `__twitter_impression`, `tracking_source`, `echobox`, `spm`, `_branch_match_id`, `_branch_referrer`, `si`. fragments like `#utm_source=…` go too; a plain `#section` stays.

per site, on top of that:

- youtube: `feature`, `pp`, `kw`
- spotify: `context`, `nd`, `dl_branch`
- twitter / x and fx/vx mirrors (`twitter.com`, `x.com`, `fxtwitter.com`, `vxtwitter.com`, `fixupx.com`, `fixvx.com`, `samekosabax.com`): `s`, `t`, `src`, `ref_src`, `ref_url`, `cn`, `a`
- instagram: `igshid`, `igsh`
- threads: `xmt`, `slof`
- tiktok: `_r`, `_t`, `_d`, `is_from_webapp`, `is_copy_url`, `sender_device`, `sender_web_id`, `web_id`, `u_code`, `preview_pb`, `timestamp`, `user_id`, `share_app_name`, `share_app_id`, `share_iid`, `share_link_id`, `share_item_id`, `social_share_type`, `source`, `checksum`, `tt_from`
- facebook: `mibextid`, `rdid`, `__tn__`, `__cft__[*]`, `__xts__[*]`, `hc_*`, `eid`, `ref`, `fref`, `refid`, `refsrc`, `ref_*`, `comment_tracking`, `notif_id`, `notif_t`, `sfnsn`, `paipv`, `eav`, `dti`, `_rdr`, `rdr`, `rdc`, `wtsid`, `acontext`
- reddit: `share_id`, `ref`, `ref_source`, `ref_campaign`, `correlation_id`, `rdt`, `$deep_link`, `$3p`, `$original_url`
- amazon: `p[fd]_rd_*`, `qid`, `srs?`, `__mk_*`, `spia`, `ms3_c`, `ie`, `refrid`, `colii?d`, `adid`, `qualifier`, `_encoding`, `ref_?`, `sprefix`, `crid`, `cv_ct_*`, `linkcode`, `linkid`, `tag`, `creativeasin`, `ascsubtag`, `aaxitk`, `hsa_cr_id`, `sb-ci-*`, `dchild`, `camp`, `creative`, `content-id`, `dib`, `dib_tag`, `social_share`, `starsleft`, `skiptwisterog`; the `/ref=…` segment of the path goes too
- aliexpress: `aff_*`, `af`, `afsmartredirect`, `algo_expid`, `algo_pvid`, `btsid`, `businesstype`, `cv`, `dp`, `gps-id`, `gatewayadapt`, `mall_affr`, `pdp_ext_f`, `pdp_npi`, `pdp_pi`, `pvid`, `scm*`, `sk`, `social_params`, `sourcetype`, `spreadtype`, `srcsns`, `terminal_id`, `tt`, `ws_ab_test`, `utparam-url`
- vk: `from`, `ref`, `ref_domain`
- yandex: `from`, `clid`, `redircnt`
- google search: `ved`, `ei`, `sa`, `usg`, `oq`, `aqs`, `gs_*`, `sclient`, `sxsrf`, `sourceid`, `uact`, `bih`, `biw`, `dpr`, `rlz`, `iflsig`, `sca_esv`, `sca_upv`, `fbs`, `ictx`, `cshid`, `gws_rd`, `source`, `ie`
- google docs and drive: `usp`
- linkedin: `trk`, `trkinfo`, `trackingid`, `refid`, `lipi`, `licu`, `midtoken`, `midsig`, `trkemail`, `rcm`
- ebay: `_trkparms`, `_trksid`, `_from`, `hash`, `mkcid`, `mkrid`, `mkevt`, `campid`, `toolid`, `customid`, `amdata`, `ssspo`, `sssrc`, `ssuid`, `widget_ver`, `itmmeta`
- medium: `source`
- github: `email_token`, `email_source`
- steam: `snr`
- netflix: `trackid`, `tctx`
- twitch: `tt_medium`, `tt_content`
- imdb: `ref_`, `pf_rd_*`
- bing: `cvid`, `form`, `sk`, `sp`, `sc`, `qs`, `qp`, `pq`, `ghsh`, `ghacc`, `ghpl`
- msn: `ocid`, `cvid`
- apple: `ign-itsc*`, `itscg`, `itsct`
- pinterest: `invite_code`, `sender`, `sfo`
- hh.ru: `hhtmfrom`, `hhtmfromlabel`, `hhtmsource`, `vss`, `swnt`, `grpos`, `ptl`, `stl`, `exp`, `plim`
- ozon: `partner`, `from`
