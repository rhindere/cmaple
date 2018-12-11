
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'ACCEPT ADDR APPEND BANG BCAST CHECK COLON COMMA DEFAULT DELETE DELETE_CHAIN DEV DROP EQ FILTER FLUSH GOTO INET INSERT IN_INTERFACE IPTABLES IPV4 IPV6 IP_ADDR IP_DESTINATION IP_SOURCE JUMP LINK LIST LIST_RULES MANGLE MASK MATCH NAT NEW_CHAIN NL NUMBER OUT_INTERFACE POLICY PORT_DESTINATION PORT_SOURCE PROTOCOL QUEUE RAW RENAME_CHAIN REPLACE RETURN SECURITY SLASH SQUARE_BRACKET SRC STAR STATE TABLE VIA WORD WS ZEROlines : line\n             | line linesline : interface_line NL\n            | interface_address NL\n            | variable_line NL\n            | iptables_line NL\n            | table_line NL\n            | chain_line NL\n            | command_line NL\n            | WORD items NL\n            | route_line NL\n            | NLline : error NLempty :items : item items\n             | itemitem : WORD\n            | NUMBER\n            | COLONinterface_line : WORD LINK itemsinterface_address : INET ADDR COLON IP_ADDR opt_bcast MASK COLON IP_ADDRopt_bcast : BCAST COLON IP_ADDR\n                 | emptyvariable_line : WORD EQ itemvariable_line : WORD EQ erroriptables_line : IPTABLES opt_table commandsopt_table : TABLE FILTER\n                 | emptyopt_table : TABLE NAT\n                 | TABLE MANGLE\n                 | TABLE RAW\n                 | TABLE SECURITYtable_line : STAR FILTER\n                  | STAR NAT\n                  | STAR MANGLE\n                  | STAR RAW\n                  | STAR SECURITYchain_line : COLON chain ACCEPT SQUARE_BRACKET NUMBER COLON NUMBER SQUARE_BRACKETchain_line : COLON chain DROP SQUARE_BRACKET NUMBER COLON NUMBER SQUARE_BRACKETchain_line : COLON chain WORD SQUARE_BRACKET NUMBER COLON NUMBER SQUARE_BRACKETcommand_line : commandscommands : append_cmd\n                | check_cmd\n                | delete_cmd\n                | insert_cmd\n                | replace_cmd\n                | list_cmd\n                | list_rules_cmd\n                | flush_cmd\n                | zero_cmd\n                | new_chain_cmd\n                | delete_chain_cmd\n                | policy_cmd\n                | rename_chain_cmdappend_cmd : APPEND chain rule_speccheck_cmd : CHECK chain rule_specdelete_cmd : DELETE chain rule_specdelete_cmd : DELETE chain NUMBERinsert_cmd : INSERT chain NUMBER rule_specinsert_cmd : INSERT chain rule_specreplace_cmd : REPLACE chain NUMBER rule_speclist_cmd : LIST chain\n                | LISTlist_rules_cmd : LIST_RULES chain\n                      | LIST_RULESflush_cmd : FLUSH chainflush_cmd : FLUSHzero_cmd : ZERO chain NUMBER\n                | ZERO chain\n                | ZEROnew_chain_cmd : NEW_CHAIN chaindelete_chain_cmd : DELETE_CHAIN chaindelete_chain_cmd : DELETE_CHAINpolicy_cmd : POLICY chain targetrename_chain_cmd : RENAME_CHAIN chain chainchain : WORDrule_spec : opt_matchesopt_matches : opt_match opt_matches\n                   | opt_matchunsupported_option : WORD unsupported_arguments\n                          | WORDunsupported_arguments : unsupported_arg unsupported_arguments\n                             | unsupported_argunsupported_arg : WORD\n                       | NUMBER\n                       | COLONopt_match : IPV4\n                 | IPV6\n                 | protocol\n                 | ip_source\n                 | ip_destination\n                 | port_source\n                 | port_destination\n                 | MATCH items\n                 | jump_target\n                 | goto_chain\n                 | in_interface\n                 | out_interface\n                 | state_option\n                 | errorprotocol : PROTOCOL itemprotocol : BANG PROTOCOL itemip_source : IP_SOURCE ip_addr_listip_source : BANG IP_SOURCE ip_addr_listip_destination : IP_DESTINATION ip_addr_listip_destination : BANG IP_DESTINATION ip_addr_listip_addr_list : ip_addr COMMA ip_addr_listip_addr_list : ip_addrip_addr : IP_ADDRip_addr : IP_ADDR SLASH NUMBERip_addr : IP_ADDR SLASH IP_ADDRport_source : PORT_SOURCE port_listport_source : BANG PORT_SOURCE port_listport_destination : PORT_DESTINATION port_listport_destination : BANG PORT_DESTINATION port_listport_list : item COLON itemport_list : item COMMA port_listport_list : itemjump_target : JUMP targetgoto_chain : GOTO chainin_interface : IN_INTERFACE WORDout_interface : OUT_INTERFACE WORDstate_option : STATE state_argstate_arg : WORDstate_arg : WORD COMMA state_argtarget : ACCEPTtarget : DROPtarget : QUEUEtarget : RETURNtarget : WORDroute_line : DEFAULT VIA IP_ADDR DEV WORDroute_line : IP_ADDR SLASH NUMBER VIA IP_ADDR DEV WORDroute_line : IP_ADDR SLASH NUMBER DEV WORD WORD WORD WORD LINK SRC IP_ADDR\n                  | IP_ADDR SLASH NUMBER DEV WORD WORD WORD WORD LINK SRC IP_ADDR WORD NUMBER'
    
_lr_action_items = {'WORD':([0,2,4,11,15,34,35,36,37,38,39,40,41,42,43,44,45,46,48,49,50,51,52,53,54,55,57,58,59,60,61,62,63,65,66,88,89,90,117,124,128,129,130,131,132,133,134,154,155,159,162,163,186,195,196,197,203,204,217,225,],[11,11,-12,55,66,66,66,66,66,66,66,66,66,66,66,66,66,66,-3,-4,-5,-6,-7,-8,-9,-17,55,55,55,-18,-19,-11,-13,98,-76,147,66,-10,55,55,55,55,147,66,173,174,176,186,187,55,55,55,204,55,55,176,216,217,222,226,]),'NL':([0,2,3,4,5,6,7,8,9,10,12,13,18,21,22,23,24,25,26,27,28,29,30,31,32,33,39,40,41,42,44,48,49,50,51,52,53,54,55,56,59,60,61,62,63,66,71,72,73,74,75,82,83,84,85,86,87,90,91,92,93,94,100,107,108,109,110,111,112,113,114,115,116,118,119,120,121,122,123,135,136,137,139,141,142,143,144,145,146,147,148,156,157,158,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,187,188,189,190,191,192,205,206,207,208,209,210,216,218,219,220,221,225,227,],[4,4,48,-12,49,50,51,52,53,54,62,63,-41,-42,-43,-44,-45,-46,-47,-48,-49,-50,-51,-52,-53,-54,-63,-65,-67,-70,-73,-3,-4,-5,-6,-7,-8,-9,-17,90,-16,-18,-19,-11,-13,-76,-33,-34,-35,-36,-37,-62,-64,-66,-69,-71,-72,-10,-20,-24,-25,-15,-26,-55,-77,-79,-87,-88,-89,-90,-91,-92,-93,-95,-96,-97,-98,-99,-100,-56,-57,-58,-60,-68,-74,-126,-127,-128,-129,-130,-75,-78,-94,-101,-103,-108,-109,-105,-112,-118,-114,-119,-120,-121,-122,-123,-124,-59,-61,-131,-102,-104,-106,-113,-115,-107,-111,-110,-116,-117,-125,-132,-21,-38,-39,-40,-133,-134,]),'error':([0,2,4,48,49,50,51,52,53,54,55,58,59,60,61,62,63,66,77,78,79,80,90,94,109,110,111,112,113,114,115,116,118,119,120,121,122,123,138,140,143,144,145,146,147,157,158,164,165,166,167,168,169,170,171,172,173,174,175,176,188,189,190,191,192,205,206,207,208,209,210,],[13,13,-12,-3,-4,-5,-6,-7,-8,-9,-17,93,-16,-18,-19,-11,-13,-76,123,123,123,123,-10,-15,123,-87,-88,-89,-90,-91,-92,-93,-95,-96,-97,-98,-99,-100,123,123,-126,-127,-128,-129,-130,-94,-101,-103,-108,-109,-105,-112,-118,-114,-119,-120,-121,-122,-123,-124,-102,-104,-106,-113,-115,-107,-111,-110,-116,-117,-125,]),'INET':([0,2,4,48,49,50,51,52,53,54,62,63,90,],[14,14,-12,-3,-4,-5,-6,-7,-8,-9,-11,-13,-10,]),'IPTABLES':([0,2,4,48,49,50,51,52,53,54,62,63,90,],[17,17,-12,-3,-4,-5,-6,-7,-8,-9,-11,-13,-10,]),'STAR':([0,2,4,48,49,50,51,52,53,54,62,63,90,],[19,19,-12,-3,-4,-5,-6,-7,-8,-9,-11,-13,-10,]),'COLON':([0,2,4,11,48,49,50,51,52,53,54,55,57,58,59,60,61,62,63,64,90,117,124,128,129,159,162,163,169,180,182,183,184,195,196,198,],[15,15,-12,61,-3,-4,-5,-6,-7,-8,-9,-17,61,61,61,-18,-19,-11,-13,95,-10,61,61,61,61,61,61,61,195,199,200,201,202,61,61,211,]),'DEFAULT':([0,2,4,48,49,50,51,52,53,54,62,63,90,],[20,20,-12,-3,-4,-5,-6,-7,-8,-9,-11,-13,-10,]),'IP_ADDR':([0,2,4,48,49,50,51,52,53,54,62,63,76,90,95,126,127,153,160,161,193,194,199,211,224,],[16,16,-12,-3,-4,-5,-6,-7,-8,-9,-11,-13,106,-10,149,166,166,185,166,166,166,206,212,218,225,]),'APPEND':([0,2,4,17,48,49,50,51,52,53,54,62,63,68,70,90,101,102,103,104,105,],[34,34,-12,-14,-3,-4,-5,-6,-7,-8,-9,-11,-13,34,-28,-10,-27,-29,-30,-31,-32,]),'CHECK':([0,2,4,17,48,49,50,51,52,53,54,62,63,68,70,90,101,102,103,104,105,],[35,35,-12,-14,-3,-4,-5,-6,-7,-8,-9,-11,-13,35,-28,-10,-27,-29,-30,-31,-32,]),'DELETE':([0,2,4,17,48,49,50,51,52,53,54,62,63,68,70,90,101,102,103,104,105,],[36,36,-12,-14,-3,-4,-5,-6,-7,-8,-9,-11,-13,36,-28,-10,-27,-29,-30,-31,-32,]),'INSERT':([0,2,4,17,48,49,50,51,52,53,54,62,63,68,70,90,101,102,103,104,105,],[37,37,-12,-14,-3,-4,-5,-6,-7,-8,-9,-11,-13,37,-28,-10,-27,-29,-30,-31,-32,]),'REPLACE':([0,2,4,17,48,49,50,51,52,53,54,62,63,68,70,90,101,102,103,104,105,],[38,38,-12,-14,-3,-4,-5,-6,-7,-8,-9,-11,-13,38,-28,-10,-27,-29,-30,-31,-32,]),'LIST':([0,2,4,17,48,49,50,51,52,53,54,62,63,68,70,90,101,102,103,104,105,],[39,39,-12,-14,-3,-4,-5,-6,-7,-8,-9,-11,-13,39,-28,-10,-27,-29,-30,-31,-32,]),'LIST_RULES':([0,2,4,17,48,49,50,51,52,53,54,62,63,68,70,90,101,102,103,104,105,],[40,40,-12,-14,-3,-4,-5,-6,-7,-8,-9,-11,-13,40,-28,-10,-27,-29,-30,-31,-32,]),'FLUSH':([0,2,4,17,48,49,50,51,52,53,54,62,63,68,70,90,101,102,103,104,105,],[41,41,-12,-14,-3,-4,-5,-6,-7,-8,-9,-11,-13,41,-28,-10,-27,-29,-30,-31,-32,]),'ZERO':([0,2,4,17,48,49,50,51,52,53,54,62,63,68,70,90,101,102,103,104,105,],[42,42,-12,-14,-3,-4,-5,-6,-7,-8,-9,-11,-13,42,-28,-10,-27,-29,-30,-31,-32,]),'NEW_CHAIN':([0,2,4,17,48,49,50,51,52,53,54,62,63,68,70,90,101,102,103,104,105,],[43,43,-12,-14,-3,-4,-5,-6,-7,-8,-9,-11,-13,43,-28,-10,-27,-29,-30,-31,-32,]),'DELETE_CHAIN':([0,2,4,17,48,49,50,51,52,53,54,62,63,68,70,90,101,102,103,104,105,],[44,44,-12,-14,-3,-4,-5,-6,-7,-8,-9,-11,-13,44,-28,-10,-27,-29,-30,-31,-32,]),'POLICY':([0,2,4,17,48,49,50,51,52,53,54,62,63,68,70,90,101,102,103,104,105,],[45,45,-12,-14,-3,-4,-5,-6,-7,-8,-9,-11,-13,45,-28,-10,-27,-29,-30,-31,-32,]),'RENAME_CHAIN':([0,2,4,17,48,49,50,51,52,53,54,62,63,68,70,90,101,102,103,104,105,],[46,46,-12,-14,-3,-4,-5,-6,-7,-8,-9,-11,-13,46,-28,-10,-27,-29,-30,-31,-32,]),'$end':([1,2,4,47,48,49,50,51,52,53,54,62,63,90,],[0,-1,-12,-2,-3,-4,-5,-6,-7,-8,-9,-11,-13,-10,]),'LINK':([11,222,],[57,223,]),'EQ':([11,],[58,]),'NUMBER':([11,55,57,58,59,60,61,66,67,79,80,81,85,117,124,128,129,150,151,152,159,162,163,194,195,196,200,201,202,226,],[60,-17,60,60,60,-18,-19,-76,99,137,138,140,141,60,60,60,60,182,183,184,60,60,60,207,60,60,213,214,215,227,]),'ADDR':([14,],[64,]),'SLASH':([16,166,],[67,194,]),'TABLE':([17,],[69,]),'FILTER':([19,69,],[71,101,]),'NAT':([19,69,],[72,102,]),'MANGLE':([19,69,],[73,103,]),'RAW':([19,69,],[74,104,]),'SECURITY':([19,69,],[75,105,]),'VIA':([20,99,],[76,153,]),'IPV4':([55,59,60,61,66,77,78,79,80,94,109,110,111,112,113,114,115,116,118,119,120,121,122,123,138,140,143,144,145,146,147,157,158,164,165,166,167,168,169,170,171,172,173,174,175,176,188,189,190,191,192,205,206,207,208,209,210,],[-17,-16,-18,-19,-76,110,110,110,110,-15,110,-87,-88,-89,-90,-91,-92,-93,-95,-96,-97,-98,-99,-100,110,110,-126,-127,-128,-129,-130,-94,-101,-103,-108,-109,-105,-112,-118,-114,-119,-120,-121,-122,-123,-124,-102,-104,-106,-113,-115,-107,-111,-110,-116,-117,-125,]),'IPV6':([55,59,60,61,66,77,78,79,80,94,109,110,111,112,113,114,115,116,118,119,120,121,122,123,138,140,143,144,145,146,147,157,158,164,165,166,167,168,169,170,171,172,173,174,175,176,188,189,190,191,192,205,206,207,208,209,210,],[-17,-16,-18,-19,-76,111,111,111,111,-15,111,-87,-88,-89,-90,-91,-92,-93,-95,-96,-97,-98,-99,-100,111,111,-126,-127,-128,-129,-130,-94,-101,-103,-108,-109,-105,-112,-118,-114,-119,-120,-121,-122,-123,-124,-102,-104,-106,-113,-115,-107,-111,-110,-116,-117,-125,]),'MATCH':([55,59,60,61,66,77,78,79,80,94,109,110,111,112,113,114,115,116,118,119,120,121,122,123,138,140,143,144,145,146,147,157,158,164,165,166,167,168,169,170,171,172,173,174,175,176,188,189,190,191,192,205,206,207,208,209,210,],[-17,-16,-18,-19,-76,117,117,117,117,-15,117,-87,-88,-89,-90,-91,-92,-93,-95,-96,-97,-98,-99,-100,117,117,-126,-127,-128,-129,-130,-94,-101,-103,-108,-109,-105,-112,-118,-114,-119,-120,-121,-122,-123,-124,-102,-104,-106,-113,-115,-107,-111,-110,-116,-117,-125,]),'PROTOCOL':([55,59,60,61,66,77,78,79,80,94,109,110,111,112,113,114,115,116,118,119,120,121,122,123,125,138,140,143,144,145,146,147,157,158,164,165,166,167,168,169,170,171,172,173,174,175,176,188,189,190,191,192,205,206,207,208,209,210,],[-17,-16,-18,-19,-76,124,124,124,124,-15,124,-87,-88,-89,-90,-91,-92,-93,-95,-96,-97,-98,-99,-100,159,124,124,-126,-127,-128,-129,-130,-94,-101,-103,-108,-109,-105,-112,-118,-114,-119,-120,-121,-122,-123,-124,-102,-104,-106,-113,-115,-107,-111,-110,-116,-117,-125,]),'BANG':([55,59,60,61,66,77,78,79,80,94,109,110,111,112,113,114,115,116,118,119,120,121,122,123,138,140,143,144,145,146,147,157,158,164,165,166,167,168,169,170,171,172,173,174,175,176,188,189,190,191,192,205,206,207,208,209,210,],[-17,-16,-18,-19,-76,125,125,125,125,-15,125,-87,-88,-89,-90,-91,-92,-93,-95,-96,-97,-98,-99,-100,125,125,-126,-127,-128,-129,-130,-94,-101,-103,-108,-109,-105,-112,-118,-114,-119,-120,-121,-122,-123,-124,-102,-104,-106,-113,-115,-107,-111,-110,-116,-117,-125,]),'IP_SOURCE':([55,59,60,61,66,77,78,79,80,94,109,110,111,112,113,114,115,116,118,119,120,121,122,123,125,138,140,143,144,145,146,147,157,158,164,165,166,167,168,169,170,171,172,173,174,175,176,188,189,190,191,192,205,206,207,208,209,210,],[-17,-16,-18,-19,-76,126,126,126,126,-15,126,-87,-88,-89,-90,-91,-92,-93,-95,-96,-97,-98,-99,-100,160,126,126,-126,-127,-128,-129,-130,-94,-101,-103,-108,-109,-105,-112,-118,-114,-119,-120,-121,-122,-123,-124,-102,-104,-106,-113,-115,-107,-111,-110,-116,-117,-125,]),'IP_DESTINATION':([55,59,60,61,66,77,78,79,80,94,109,110,111,112,113,114,115,116,118,119,120,121,122,123,125,138,140,143,144,145,146,147,157,158,164,165,166,167,168,169,170,171,172,173,174,175,176,188,189,190,191,192,205,206,207,208,209,210,],[-17,-16,-18,-19,-76,127,127,127,127,-15,127,-87,-88,-89,-90,-91,-92,-93,-95,-96,-97,-98,-99,-100,161,127,127,-126,-127,-128,-129,-130,-94,-101,-103,-108,-109,-105,-112,-118,-114,-119,-120,-121,-122,-123,-124,-102,-104,-106,-113,-115,-107,-111,-110,-116,-117,-125,]),'PORT_SOURCE':([55,59,60,61,66,77,78,79,80,94,109,110,111,112,113,114,115,116,118,119,120,121,122,123,125,138,140,143,144,145,146,147,157,158,164,165,166,167,168,169,170,171,172,173,174,175,176,188,189,190,191,192,205,206,207,208,209,210,],[-17,-16,-18,-19,-76,128,128,128,128,-15,128,-87,-88,-89,-90,-91,-92,-93,-95,-96,-97,-98,-99,-100,162,128,128,-126,-127,-128,-129,-130,-94,-101,-103,-108,-109,-105,-112,-118,-114,-119,-120,-121,-122,-123,-124,-102,-104,-106,-113,-115,-107,-111,-110,-116,-117,-125,]),'PORT_DESTINATION':([55,59,60,61,66,77,78,79,80,94,109,110,111,112,113,114,115,116,118,119,120,121,122,123,125,138,140,143,144,145,146,147,157,158,164,165,166,167,168,169,170,171,172,173,174,175,176,188,189,190,191,192,205,206,207,208,209,210,],[-17,-16,-18,-19,-76,129,129,129,129,-15,129,-87,-88,-89,-90,-91,-92,-93,-95,-96,-97,-98,-99,-100,163,129,129,-126,-127,-128,-129,-130,-94,-101,-103,-108,-109,-105,-112,-118,-114,-119,-120,-121,-122,-123,-124,-102,-104,-106,-113,-115,-107,-111,-110,-116,-117,-125,]),'JUMP':([55,59,60,61,66,77,78,79,80,94,109,110,111,112,113,114,115,116,118,119,120,121,122,123,138,140,143,144,145,146,147,157,158,164,165,166,167,168,169,170,171,172,173,174,175,176,188,189,190,191,192,205,206,207,208,209,210,],[-17,-16,-18,-19,-76,130,130,130,130,-15,130,-87,-88,-89,-90,-91,-92,-93,-95,-96,-97,-98,-99,-100,130,130,-126,-127,-128,-129,-130,-94,-101,-103,-108,-109,-105,-112,-118,-114,-119,-120,-121,-122,-123,-124,-102,-104,-106,-113,-115,-107,-111,-110,-116,-117,-125,]),'GOTO':([55,59,60,61,66,77,78,79,80,94,109,110,111,112,113,114,115,116,118,119,120,121,122,123,138,140,143,144,145,146,147,157,158,164,165,166,167,168,169,170,171,172,173,174,175,176,188,189,190,191,192,205,206,207,208,209,210,],[-17,-16,-18,-19,-76,131,131,131,131,-15,131,-87,-88,-89,-90,-91,-92,-93,-95,-96,-97,-98,-99,-100,131,131,-126,-127,-128,-129,-130,-94,-101,-103,-108,-109,-105,-112,-118,-114,-119,-120,-121,-122,-123,-124,-102,-104,-106,-113,-115,-107,-111,-110,-116,-117,-125,]),'IN_INTERFACE':([55,59,60,61,66,77,78,79,80,94,109,110,111,112,113,114,115,116,118,119,120,121,122,123,138,140,143,144,145,146,147,157,158,164,165,166,167,168,169,170,171,172,173,174,175,176,188,189,190,191,192,205,206,207,208,209,210,],[-17,-16,-18,-19,-76,132,132,132,132,-15,132,-87,-88,-89,-90,-91,-92,-93,-95,-96,-97,-98,-99,-100,132,132,-126,-127,-128,-129,-130,-94,-101,-103,-108,-109,-105,-112,-118,-114,-119,-120,-121,-122,-123,-124,-102,-104,-106,-113,-115,-107,-111,-110,-116,-117,-125,]),'OUT_INTERFACE':([55,59,60,61,66,77,78,79,80,94,109,110,111,112,113,114,115,116,118,119,120,121,122,123,138,140,143,144,145,146,147,157,158,164,165,166,167,168,169,170,171,172,173,174,175,176,188,189,190,191,192,205,206,207,208,209,210,],[-17,-16,-18,-19,-76,133,133,133,133,-15,133,-87,-88,-89,-90,-91,-92,-93,-95,-96,-97,-98,-99,-100,133,133,-126,-127,-128,-129,-130,-94,-101,-103,-108,-109,-105,-112,-118,-114,-119,-120,-121,-122,-123,-124,-102,-104,-106,-113,-115,-107,-111,-110,-116,-117,-125,]),'STATE':([55,59,60,61,66,77,78,79,80,94,109,110,111,112,113,114,115,116,118,119,120,121,122,123,138,140,143,144,145,146,147,157,158,164,165,166,167,168,169,170,171,172,173,174,175,176,188,189,190,191,192,205,206,207,208,209,210,],[-17,-16,-18,-19,-76,134,134,134,134,-15,134,-87,-88,-89,-90,-91,-92,-93,-95,-96,-97,-98,-99,-100,134,134,-126,-127,-128,-129,-130,-94,-101,-103,-108,-109,-105,-112,-118,-114,-119,-120,-121,-122,-123,-124,-102,-104,-106,-113,-115,-107,-111,-110,-116,-117,-125,]),'COMMA':([55,60,61,165,166,169,176,206,207,],[-17,-18,-19,193,-109,196,197,-111,-110,]),'ACCEPT':([65,66,88,130,],[96,-76,143,143,]),'DROP':([65,66,88,130,],[97,-76,144,144,]),'QUEUE':([66,88,130,],[-76,145,145,]),'RETURN':([66,88,130,],[-76,146,146,]),'SQUARE_BRACKET':([96,97,98,213,214,215,],[150,151,152,219,220,221,]),'DEV':([99,106,185,],[154,155,203,]),'BCAST':([149,],[180,]),'MASK':([149,179,181,212,],[-14,198,-23,-22,]),'SRC':([223,],[224,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'lines':([0,2,],[1,47,]),'line':([0,2,],[2,2,]),'interface_line':([0,2,],[3,3,]),'interface_address':([0,2,],[5,5,]),'variable_line':([0,2,],[6,6,]),'iptables_line':([0,2,],[7,7,]),'table_line':([0,2,],[8,8,]),'chain_line':([0,2,],[9,9,]),'command_line':([0,2,],[10,10,]),'route_line':([0,2,],[12,12,]),'commands':([0,2,68,],[18,18,100,]),'append_cmd':([0,2,68,],[21,21,21,]),'check_cmd':([0,2,68,],[22,22,22,]),'delete_cmd':([0,2,68,],[23,23,23,]),'insert_cmd':([0,2,68,],[24,24,24,]),'replace_cmd':([0,2,68,],[25,25,25,]),'list_cmd':([0,2,68,],[26,26,26,]),'list_rules_cmd':([0,2,68,],[27,27,27,]),'flush_cmd':([0,2,68,],[28,28,28,]),'zero_cmd':([0,2,68,],[29,29,29,]),'new_chain_cmd':([0,2,68,],[30,30,30,]),'delete_chain_cmd':([0,2,68,],[31,31,31,]),'policy_cmd':([0,2,68,],[32,32,32,]),'rename_chain_cmd':([0,2,68,],[33,33,33,]),'items':([11,57,59,117,],[56,91,94,157,]),'item':([11,57,58,59,117,124,128,129,159,162,163,195,196,],[59,59,92,59,59,158,169,169,188,169,169,208,169,]),'chain':([15,34,35,36,37,38,39,40,41,42,43,44,45,46,89,131,],[65,77,78,79,80,81,82,83,84,85,86,87,88,89,148,172,]),'opt_table':([17,],[68,]),'empty':([17,149,],[70,181,]),'rule_spec':([77,78,79,80,138,140,],[107,135,136,139,177,178,]),'opt_matches':([77,78,79,80,109,138,140,],[108,108,108,108,156,108,108,]),'opt_match':([77,78,79,80,109,138,140,],[109,109,109,109,109,109,109,]),'protocol':([77,78,79,80,109,138,140,],[112,112,112,112,112,112,112,]),'ip_source':([77,78,79,80,109,138,140,],[113,113,113,113,113,113,113,]),'ip_destination':([77,78,79,80,109,138,140,],[114,114,114,114,114,114,114,]),'port_source':([77,78,79,80,109,138,140,],[115,115,115,115,115,115,115,]),'port_destination':([77,78,79,80,109,138,140,],[116,116,116,116,116,116,116,]),'jump_target':([77,78,79,80,109,138,140,],[118,118,118,118,118,118,118,]),'goto_chain':([77,78,79,80,109,138,140,],[119,119,119,119,119,119,119,]),'in_interface':([77,78,79,80,109,138,140,],[120,120,120,120,120,120,120,]),'out_interface':([77,78,79,80,109,138,140,],[121,121,121,121,121,121,121,]),'state_option':([77,78,79,80,109,138,140,],[122,122,122,122,122,122,122,]),'target':([88,130,],[142,171,]),'ip_addr_list':([126,127,160,161,193,],[164,167,189,190,205,]),'ip_addr':([126,127,160,161,193,],[165,165,165,165,165,]),'port_list':([128,129,162,163,196,],[168,170,191,192,209,]),'state_arg':([134,197,],[175,210,]),'opt_bcast':([149,],[179,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> lines","S'",1,None,None,None),
  ('lines -> line','lines',1,'p_lines','IpTablesYacc.py',295),
  ('lines -> line lines','lines',2,'p_lines','IpTablesYacc.py',296),
  ('line -> interface_line NL','line',2,'p_line','IpTablesYacc.py',300),
  ('line -> interface_address NL','line',2,'p_line','IpTablesYacc.py',301),
  ('line -> variable_line NL','line',2,'p_line','IpTablesYacc.py',302),
  ('line -> iptables_line NL','line',2,'p_line','IpTablesYacc.py',303),
  ('line -> table_line NL','line',2,'p_line','IpTablesYacc.py',304),
  ('line -> chain_line NL','line',2,'p_line','IpTablesYacc.py',305),
  ('line -> command_line NL','line',2,'p_line','IpTablesYacc.py',306),
  ('line -> WORD items NL','line',3,'p_line','IpTablesYacc.py',307),
  ('line -> route_line NL','line',2,'p_line','IpTablesYacc.py',308),
  ('line -> NL','line',1,'p_line','IpTablesYacc.py',309),
  ('line -> error NL','line',2,'p_line_error','IpTablesYacc.py',315),
  ('empty -> <empty>','empty',0,'p_empty','IpTablesYacc.py',319),
  ('items -> item items','items',2,'p_items','IpTablesYacc.py',324),
  ('items -> item','items',1,'p_items','IpTablesYacc.py',325),
  ('item -> WORD','item',1,'p_item','IpTablesYacc.py',329),
  ('item -> NUMBER','item',1,'p_item','IpTablesYacc.py',330),
  ('item -> COLON','item',1,'p_item','IpTablesYacc.py',331),
  ('interface_line -> WORD LINK items','interface_line',3,'p_interface_line','IpTablesYacc.py',339),
  ('interface_address -> INET ADDR COLON IP_ADDR opt_bcast MASK COLON IP_ADDR','interface_address',8,'p_interface_address','IpTablesYacc.py',345),
  ('opt_bcast -> BCAST COLON IP_ADDR','opt_bcast',3,'p_opt_bcast','IpTablesYacc.py',352),
  ('opt_bcast -> empty','opt_bcast',1,'p_opt_bcast','IpTablesYacc.py',353),
  ('variable_line -> WORD EQ item','variable_line',3,'p_variable_line_1','IpTablesYacc.py',359),
  ('variable_line -> WORD EQ error','variable_line',3,'p_variable_line_2','IpTablesYacc.py',365),
  ('iptables_line -> IPTABLES opt_table commands','iptables_line',3,'p_iptables_line','IpTablesYacc.py',372),
  ('opt_table -> TABLE FILTER','opt_table',2,'p_opt_table1','IpTablesYacc.py',377),
  ('opt_table -> empty','opt_table',1,'p_opt_table1','IpTablesYacc.py',378),
  ('opt_table -> TABLE NAT','opt_table',2,'p_opt_table2','IpTablesYacc.py',383),
  ('opt_table -> TABLE MANGLE','opt_table',2,'p_opt_table2','IpTablesYacc.py',384),
  ('opt_table -> TABLE RAW','opt_table',2,'p_opt_table2','IpTablesYacc.py',385),
  ('opt_table -> TABLE SECURITY','opt_table',2,'p_opt_table2','IpTablesYacc.py',386),
  ('table_line -> STAR FILTER','table_line',2,'p_table_line1','IpTablesYacc.py',394),
  ('table_line -> STAR NAT','table_line',2,'p_table_line1','IpTablesYacc.py',395),
  ('table_line -> STAR MANGLE','table_line',2,'p_table_line1','IpTablesYacc.py',396),
  ('table_line -> STAR RAW','table_line',2,'p_table_line1','IpTablesYacc.py',397),
  ('table_line -> STAR SECURITY','table_line',2,'p_table_line1','IpTablesYacc.py',398),
  ('chain_line -> COLON chain ACCEPT SQUARE_BRACKET NUMBER COLON NUMBER SQUARE_BRACKET','chain_line',8,'p_chain_line1','IpTablesYacc.py',403),
  ('chain_line -> COLON chain DROP SQUARE_BRACKET NUMBER COLON NUMBER SQUARE_BRACKET','chain_line',8,'p_chain_line2','IpTablesYacc.py',410),
  ('chain_line -> COLON chain WORD SQUARE_BRACKET NUMBER COLON NUMBER SQUARE_BRACKET','chain_line',8,'p_chain_line3','IpTablesYacc.py',417),
  ('command_line -> commands','command_line',1,'p_command_line','IpTablesYacc.py',423),
  ('commands -> append_cmd','commands',1,'p_statement','IpTablesYacc.py',430),
  ('commands -> check_cmd','commands',1,'p_statement','IpTablesYacc.py',431),
  ('commands -> delete_cmd','commands',1,'p_statement','IpTablesYacc.py',432),
  ('commands -> insert_cmd','commands',1,'p_statement','IpTablesYacc.py',433),
  ('commands -> replace_cmd','commands',1,'p_statement','IpTablesYacc.py',434),
  ('commands -> list_cmd','commands',1,'p_statement','IpTablesYacc.py',435),
  ('commands -> list_rules_cmd','commands',1,'p_statement','IpTablesYacc.py',436),
  ('commands -> flush_cmd','commands',1,'p_statement','IpTablesYacc.py',437),
  ('commands -> zero_cmd','commands',1,'p_statement','IpTablesYacc.py',438),
  ('commands -> new_chain_cmd','commands',1,'p_statement','IpTablesYacc.py',439),
  ('commands -> delete_chain_cmd','commands',1,'p_statement','IpTablesYacc.py',440),
  ('commands -> policy_cmd','commands',1,'p_statement','IpTablesYacc.py',441),
  ('commands -> rename_chain_cmd','commands',1,'p_statement','IpTablesYacc.py',442),
  ('append_cmd -> APPEND chain rule_spec','append_cmd',3,'p_append_cmd','IpTablesYacc.py',446),
  ('check_cmd -> CHECK chain rule_spec','check_cmd',3,'p_check_cmd','IpTablesYacc.py',455),
  ('delete_cmd -> DELETE chain rule_spec','delete_cmd',3,'p_delete_cmd1','IpTablesYacc.py',460),
  ('delete_cmd -> DELETE chain NUMBER','delete_cmd',3,'p_delete_cmd2','IpTablesYacc.py',467),
  ('insert_cmd -> INSERT chain NUMBER rule_spec','insert_cmd',4,'p_insert_cmd1','IpTablesYacc.py',474),
  ('insert_cmd -> INSERT chain rule_spec','insert_cmd',3,'p_insert_cmd2','IpTablesYacc.py',483),
  ('replace_cmd -> REPLACE chain NUMBER rule_spec','replace_cmd',4,'p_replace_cmd','IpTablesYacc.py',492),
  ('list_cmd -> LIST chain','list_cmd',2,'p_list_cmd','IpTablesYacc.py',499),
  ('list_cmd -> LIST','list_cmd',1,'p_list_cmd','IpTablesYacc.py',500),
  ('list_rules_cmd -> LIST_RULES chain','list_rules_cmd',2,'p_list_rules_cmd','IpTablesYacc.py',505),
  ('list_rules_cmd -> LIST_RULES','list_rules_cmd',1,'p_list_rules_cmd','IpTablesYacc.py',506),
  ('flush_cmd -> FLUSH chain','flush_cmd',2,'p_flush_cmd1','IpTablesYacc.py',511),
  ('flush_cmd -> FLUSH','flush_cmd',1,'p_flush_cmd2','IpTablesYacc.py',517),
  ('zero_cmd -> ZERO chain NUMBER','zero_cmd',3,'p_zero_cmd','IpTablesYacc.py',523),
  ('zero_cmd -> ZERO chain','zero_cmd',2,'p_zero_cmd','IpTablesYacc.py',524),
  ('zero_cmd -> ZERO','zero_cmd',1,'p_zero_cmd','IpTablesYacc.py',525),
  ('new_chain_cmd -> NEW_CHAIN chain','new_chain_cmd',2,'p_new_chain_cmd','IpTablesYacc.py',529),
  ('delete_chain_cmd -> DELETE_CHAIN chain','delete_chain_cmd',2,'p_delete_chain_cmd1','IpTablesYacc.py',535),
  ('delete_chain_cmd -> DELETE_CHAIN','delete_chain_cmd',1,'p_delete_chain_cmd2','IpTablesYacc.py',541),
  ('policy_cmd -> POLICY chain target','policy_cmd',3,'p_policy_cmd','IpTablesYacc.py',547),
  ('rename_chain_cmd -> RENAME_CHAIN chain chain','rename_chain_cmd',3,'p_rename_chain_cmd','IpTablesYacc.py',553),
  ('chain -> WORD','chain',1,'p_chain','IpTablesYacc.py',562),
  ('rule_spec -> opt_matches','rule_spec',1,'p_rule_spec','IpTablesYacc.py',567),
  ('opt_matches -> opt_match opt_matches','opt_matches',2,'p_opt_matches','IpTablesYacc.py',571),
  ('opt_matches -> opt_match','opt_matches',1,'p_opt_matches','IpTablesYacc.py',572),
  ('unsupported_option -> WORD unsupported_arguments','unsupported_option',2,'p_unsupported_option','IpTablesYacc.py',576),
  ('unsupported_option -> WORD','unsupported_option',1,'p_unsupported_option','IpTablesYacc.py',577),
  ('unsupported_arguments -> unsupported_arg unsupported_arguments','unsupported_arguments',2,'p_unsupported_arguments','IpTablesYacc.py',581),
  ('unsupported_arguments -> unsupported_arg','unsupported_arguments',1,'p_unsupported_arguments','IpTablesYacc.py',582),
  ('unsupported_arg -> WORD','unsupported_arg',1,'p_unsupported_arg','IpTablesYacc.py',586),
  ('unsupported_arg -> NUMBER','unsupported_arg',1,'p_unsupported_arg','IpTablesYacc.py',587),
  ('unsupported_arg -> COLON','unsupported_arg',1,'p_unsupported_arg','IpTablesYacc.py',588),
  ('opt_match -> IPV4','opt_match',1,'p_opt_match','IpTablesYacc.py',592),
  ('opt_match -> IPV6','opt_match',1,'p_opt_match','IpTablesYacc.py',593),
  ('opt_match -> protocol','opt_match',1,'p_opt_match','IpTablesYacc.py',594),
  ('opt_match -> ip_source','opt_match',1,'p_opt_match','IpTablesYacc.py',595),
  ('opt_match -> ip_destination','opt_match',1,'p_opt_match','IpTablesYacc.py',596),
  ('opt_match -> port_source','opt_match',1,'p_opt_match','IpTablesYacc.py',597),
  ('opt_match -> port_destination','opt_match',1,'p_opt_match','IpTablesYacc.py',598),
  ('opt_match -> MATCH items','opt_match',2,'p_opt_match','IpTablesYacc.py',599),
  ('opt_match -> jump_target','opt_match',1,'p_opt_match','IpTablesYacc.py',600),
  ('opt_match -> goto_chain','opt_match',1,'p_opt_match','IpTablesYacc.py',601),
  ('opt_match -> in_interface','opt_match',1,'p_opt_match','IpTablesYacc.py',602),
  ('opt_match -> out_interface','opt_match',1,'p_opt_match','IpTablesYacc.py',603),
  ('opt_match -> state_option','opt_match',1,'p_opt_match','IpTablesYacc.py',604),
  ('opt_match -> error','opt_match',1,'p_opt_match','IpTablesYacc.py',605),
  ('protocol -> PROTOCOL item','protocol',2,'p_protocol_1','IpTablesYacc.py',609),
  ('protocol -> BANG PROTOCOL item','protocol',3,'p_protocol_2','IpTablesYacc.py',614),
  ('ip_source -> IP_SOURCE ip_addr_list','ip_source',2,'p_ip_source_1','IpTablesYacc.py',619),
  ('ip_source -> BANG IP_SOURCE ip_addr_list','ip_source',3,'p_ip_source_2','IpTablesYacc.py',625),
  ('ip_destination -> IP_DESTINATION ip_addr_list','ip_destination',2,'p_ip_dest_1','IpTablesYacc.py',631),
  ('ip_destination -> BANG IP_DESTINATION ip_addr_list','ip_destination',3,'p_ip_dest_2','IpTablesYacc.py',637),
  ('ip_addr_list -> ip_addr COMMA ip_addr_list','ip_addr_list',3,'p_ip_addr_list1','IpTablesYacc.py',643),
  ('ip_addr_list -> ip_addr','ip_addr_list',1,'p_ip_addr_list2','IpTablesYacc.py',648),
  ('ip_addr -> IP_ADDR','ip_addr',1,'p_ip_addr1','IpTablesYacc.py',653),
  ('ip_addr -> IP_ADDR SLASH NUMBER','ip_addr',3,'p_ip_addr2','IpTablesYacc.py',658),
  ('ip_addr -> IP_ADDR SLASH IP_ADDR','ip_addr',3,'p_ip_addr3','IpTablesYacc.py',663),
  ('port_source -> PORT_SOURCE port_list','port_source',2,'p_port_source_1','IpTablesYacc.py',668),
  ('port_source -> BANG PORT_SOURCE port_list','port_source',3,'p_port_source_2','IpTablesYacc.py',677),
  ('port_destination -> PORT_DESTINATION port_list','port_destination',2,'p_port_destination_1','IpTablesYacc.py',686),
  ('port_destination -> BANG PORT_DESTINATION port_list','port_destination',3,'p_port_destination_2','IpTablesYacc.py',695),
  ('port_list -> item COLON item','port_list',3,'p_port_list1','IpTablesYacc.py',704),
  ('port_list -> item COMMA port_list','port_list',3,'p_port_list2','IpTablesYacc.py',709),
  ('port_list -> item','port_list',1,'p_port_list3','IpTablesYacc.py',714),
  ('jump_target -> JUMP target','jump_target',2,'p_jump_target','IpTablesYacc.py',719),
  ('goto_chain -> GOTO chain','goto_chain',2,'p_goto_chain','IpTablesYacc.py',724),
  ('in_interface -> IN_INTERFACE WORD','in_interface',2,'p_in_interface','IpTablesYacc.py',729),
  ('out_interface -> OUT_INTERFACE WORD','out_interface',2,'p_out_interface','IpTablesYacc.py',734),
  ('state_option -> STATE state_arg','state_option',2,'p_state_option','IpTablesYacc.py',739),
  ('state_arg -> WORD','state_arg',1,'p_state_arg1','IpTablesYacc.py',745),
  ('state_arg -> WORD COMMA state_arg','state_arg',3,'p_state_arg2','IpTablesYacc.py',750),
  ('target -> ACCEPT','target',1,'p_target1','IpTablesYacc.py',755),
  ('target -> DROP','target',1,'p_target2','IpTablesYacc.py',760),
  ('target -> QUEUE','target',1,'p_target3','IpTablesYacc.py',765),
  ('target -> RETURN','target',1,'p_target4','IpTablesYacc.py',770),
  ('target -> WORD','target',1,'p_target5','IpTablesYacc.py',775),
  ('route_line -> DEFAULT VIA IP_ADDR DEV WORD','route_line',5,'p_default_route_line','IpTablesYacc.py',782),
  ('route_line -> IP_ADDR SLASH NUMBER VIA IP_ADDR DEV WORD','route_line',7,'p_route_line2','IpTablesYacc.py',798),
  ('route_line -> IP_ADDR SLASH NUMBER DEV WORD WORD WORD WORD LINK SRC IP_ADDR','route_line',11,'p_route_line3','IpTablesYacc.py',812),
  ('route_line -> IP_ADDR SLASH NUMBER DEV WORD WORD WORD WORD LINK SRC IP_ADDR WORD NUMBER','route_line',13,'p_route_line3','IpTablesYacc.py',813),
]
