# -*- coding: utf-8 -*-
# @Author: JinZhang
# @Date:   2019-04-24 10:11:53
# @Last Modified by:   JinZhang
# @Last Modified time: 2019-07-19 18:44:29

import json
import hashlib

stageKeyMap = {
	"kaishiyouxi" : "GameStart",
	"dingzhuang" : "DingZhuang",
	"zhitou" : "ZhiTou",
	"fapai" : "DealCard",
	"jiesuan" : "Settle",
	"jieshuyouxi" : "GameEnd",
};

nodeKeyMap = {
	"onStart" : "on_start",
	"opUsers" : "get_next_op_user",
	"opInfo" : "set_op_info",
	"opCheck" : "wait_op_msg",
	"opResult" : "set_op_result",
	"opNext" : "get_next_node",
	"onEnd" : "on_end",
};

nodeSeqKeyMap = {
	"on_start" : "RuleSeq",
	"get_next_op_user" : "RulePriority",
	"set_op_info" : "RulePriority",
	"wait_op_msg" : "RuleSeq",
	"set_op_result" : "RuleSeq",
	"get_next_node" : "RulePriority",
	"on_end" : "RuleSeq",
};

opCodeKeyMap = {
	u"过" : "Pass",
	u"出牌" : "Out",
	u"抓牌" : "Grab",
	u"分张" : "FenZhang",
	u"吃牌" : "Chi",
	u"碰牌" : "Peng",
	u"暗杠" : "AnGang",
	u"直杠" : "PengGang",
	u"补杠" : "BuGang",
	u"点炮胡" : "Hu",
	u"自摸" : "ZiMo",
	u"抢杠胡" : "QiangHu",
	u"听牌" : "Ting",
	u"夹听" : "JiaTing",
	u"翻宝" : "FanBao",
	u"看宝" : "KanBao",
	u"换宝" : "HuanBao",
};

baseKeyMap = {
	"playerNumber" : "PlayerNumber",
	"totalCards" : "TotalCards",
	"zhuapai" : "Grab",
	"chupai" : "Out",
	"chipai" : "Chi",
	"pengpai" : "Peng",
	"gangpai" : "Gang",
	"baoting" : "Ting",
	"hupai" : "Hu",
	"jichupaixing" : "JiChuPaiXing",
	"tihuanpaizhang" : "ReplaceToCheckOp",
	"hutinggonggongjiance" : "CheckHuGroupCondition",
	"fenzhang" : "FenZhang",
	"liuju" : "LiuJu",
	"huanbao" : "HuanBao",
	"kanbao" : "KanBao",
	"caozuojianguolv" : "FilterOpInfo",
};

nameIdxMap = {}
def getIdByName(name):
	if name not in nameIdxMap:
		nameIdxMap[name] = 0;
	nameIdxMap[name] += 1;
	key = "_".join([name, str(nameIdxMap[name])])
	hm = hashlib.md5();
	hm.update(key.encode("utf-8"))
	return hm.hexdigest();

def insertTree2Pcfg(pcfg, tree):
	pcfg["trees"].append(tree);

def getGameTree(cfg):
	gid = getIdByName("Game");
	tree = {
		"title": "Game",
		"description": "game",
		"root": gid,
		"properties": {},
		"nodes": {
			gid : {
				"id" : gid,
				"name" : "Game",
				"title" : "Game",
				"children": [],
			},
		},
	};
	for k in cfg["stages"]:
		name = stageKeyMap.get(k, "Stage");
		rid = getIdByName(k);
		stage = {
			"id" : rid,
			"name" : name,
			"title" : name,
			"description" : k,
			"properties": {},
			"children": [],
		};
		if k == "dapai" and "dapai" in cfg["process"]:
			setDaPaiCfg(tree["nodes"], k, stage["children"], cfg["process"]["dapai"]);
		if k == "jiesuan":
			stage["properties"]["settleTypes"] = "Fan;Gang;";
		tree["nodes"][rid] = stage;
		tree["nodes"][gid]["children"].append(rid);
	return tree;

def setDaPaiCfg(nodes, dpKey, dpChildren, cfg):
	pid2indexMap = {}; # 流程id对应位置信息
	totalPptsList = []; # 所有参数列表
	cd = dpChildren;
	for i in range(len(cfg)):
		p = cfg[i];
		pid2indexMap[p["id"]] = i;
		ikey = "-".join([dpKey+"_process", str(i)]);
		rid = getIdByName(ikey);
		cd.append(rid);
		nodes[rid] = {
			"id" : rid,
			"name": "Process",
			"title" : str(i),
			"children" : [],
		};
		cdcd = nodes[rid]["children"];
		for k,v in nodeKeyMap.items():
			if k in p:
				if len(p[k]) > 0:
					vkey = "-".join([ikey, v]);
					rid1 = getIdByName(vkey);
					cdcd.append(rid1);
					nodes[rid1] = {
						"id" : rid1,
						"name": nodeSeqKeyMap[v],
						"title" : v,
						"children" : [],
					}
					# 根据priority字段，排序数据
					rl = sorted(p[k][0], key=lambda r:r["priority"]);
					for j in range(len(rl)):
						r = rl[j];
						name = r["id"];
						rid2 = getIdByName(name);
						rule = {
							"id" : rid2,
							"name" : name,
							"title" : name,
							"properties" : getRuleArgs(r.get("args", [])),
						};
						totalPptsList.append(rule["properties"]);
						nodes[rid1]["children"].append(rid2);
						nodes[rid2] = rule;
	# 转换格式
	formatPptsList(totalPptsList, [pid2indexMap, opCodeKeyMap]);
	# 转换成字符串
	# for k in ppts:
	# 	pptsp = ppts[k]["properties"];
	# 	for k1 in pptsp:
	# 		for k2 in pptsp[k1]["properties"]:
	# 			pptsp[k1]["properties"][k2] = json.dumps(pptsp[k1]["properties"][k2]);
	# 		pptsp[k1] = json.dumps(pptsp[k1]);
	# 	ppts[k] = json.dumps(ppts[k]);
	# return ppts;

# 获取规则参数
def getRuleArgs(args):
	properties = {};
	for i in range(len(args)):
		val = args[i];
		if not isinstance(val, int) and val.isdigit():
			properties[str(i)] = int(val);
		else:
			properties[str(i)] = val;
	return properties;

# 转换格式
def formatPptsList(totalPptsList, keyMapList = []):
	for pro in totalPptsList:
		for k,v in pro.items():
			for keyMap in keyMapList:
				if v in keyMap:
					pro[k] = keyMap[v];
					break;

def insertBaseRuleTrees(projectCfg, cfg, bKeyMap = None, rootName = "Sequence"):
	if not bKeyMap:
		bKeyMap = baseKeyMap;
	for k in bKeyMap:
		if k in cfg:
			totalPptsList = []; # 所有参数列表
			treeChildren = [];
			rootId = getIdByName(rootName)
			tree = {
				"title" : bKeyMap[k],
				"root" : rootId,
				"nodes": {
					rootId: {
						"id" : rootId,
						"name": rootName,
						"title" : rootName,
						"children": treeChildren,
					},
				},
			};
			for r in cfg[k]:
				name = r["id"];
				rid = getIdByName(name);
				rule = {
					"id" : rid,
					"name": name,
					"title" : name,
					"description": "",
					"properties": getRuleArgs(r.get("args", [])),
				};
				totalPptsList.append(rule["properties"]);
				tree["nodes"][rule["id"]] = rule;
				treeChildren.append(rule["id"]);
			# 转换格式
			formatPptsList(totalPptsList, [opCodeKeyMap]);
			insertTree2Pcfg(projectCfg, tree);

def insertRobotRuleTrees(projectCfg, robotCfg):
	bKeyMap = {};
	for k in robotCfg:
		if k in ["RobotOperation"]:
			insertRobotProcess(projectCfg, k, robotCfg[k]);
		elif k.find("RobotCombination") != -1:
			insertBaseRuleTrees(projectCfg, robotCfg, bKeyMap = {k:k}, rootName = "Priority");
		else:
			bKeyMap[k] = k;
	insertBaseRuleTrees(projectCfg, robotCfg, bKeyMap = bKeyMap);

def insertRobotProcess(projectCfg, key, cfg):
	pptid = getIdByName("RobotProcess");
	ppt = {
		"id" : pptid,
		"name": "RobotProcess",
		"title" : RobotProcess,
		"properties" : {},
		"children" : [],
	};
	pptp = ppt["properties"];
	for k,v in cfg.items():
		if len(v) > 0:
			pptp[k] = {
				"properties": {},
			}
			# 根据priority字段，排序数据
			rl = sorted(v, key=lambda r:r["priority"]);
			for j in range(len(rl)):
				r = rl[j];
				name = r["id"];
				rid = getIdByName(name);
				rule = {
					"id" : rid,
					"name" : name,
					"title" : name,
					"properties" : getRuleArgs(r.get("args", [])),
				};
				pptp[k]["properties"][str(j)] = rule;
	# 转换成字符串
	for k1 in pptp:
		for k2 in pptp[k1]["properties"]:
			pptp[k1]["properties"][k2] = json.dumps(pptp[k1]["properties"][k2]);
		pptp[k1] = json.dumps(pptp[k1]);
	# 插入树到项目配置中
	insertTree2Pcfg(projectCfg, {
		"title" : key,
		"root" : pptid,
		"nodes": {
			pptid: ppt,
		},
	});


if __name__ == '__main__':
	# 设置转换模式
	mode = "n"; # "a"->转换所有配置； "n"->转换除机器人外的配置； "r"->只转换机器人配置；

	# Game树
	projectCfg = {
		"trees" : [],
	};
	# 转换GameConfig配置
	if mode in ["a", "n"]:
		with open("GameConfig.json", "rb") as f:
			cfg = json.load(f);
		insertTree2Pcfg(projectCfg, getGameTree(cfg));
		insertBaseRuleTrees(projectCfg, cfg);
		# 合并旧配置【如结算】
		with open("tree.json", "rb") as f:
			treeCfg = json.load(f);
		for tree in treeCfg.get("trees", []):
			insertTree2Pcfg(projectCfg, tree);
	# 转换robot配置
	if mode in ["a", "r"]:
		with open("robot.json", "rb") as f:
			robotCfg = json.load(f);
		insertRobotRuleTrees(projectCfg, robotCfg.get("robot", {})); # 插入机器人规则
	# 输出配置
	with open("project.json", "wb") as f:
		f.write(json.dumps(projectCfg, sort_keys = True, indent = 2, separators=(',', ':')).encode("utf-8"));