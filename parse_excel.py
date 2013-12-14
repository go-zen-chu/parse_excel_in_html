# coding:utf-8
import os
from os import path
import sys
import re
import xlrd
import json
import codecs

'''
24年産水陸稲の時期別作柄及び収穫量（全国農業地域別・都道府県別）_水陸稲計
http://www.e-stat.go.jp/SG1/estat/Xlsdl.do?sinfid=000021160231

24年産麦類（子実用）の収穫量（全国農業地域別・都道府県別）_4麦計
http://www.e-stat.go.jp/SG1/estat/Xlsdl.do?sinfid=000021160241

24年産豆類（乾燥子実）及びそばの収穫量（全国農業地域別・都道府県別）_大豆
http://www.e-stat.go.jp/SG1/estat/Xlsdl.do?sinfid=000021160247

を解析するスクリプト
'''
def rm_unneed_char(u_str):
	'''全角の数字や空白、カタカナを削除'''
	return re.sub(u'[０１２３４５６７８９（）0123456789()アイウエオ　 ]+', '', u_str)

def crop_report_genre(u_str):
	'''全角スペースや半角スペースで区切られた最後の文字列を取得'''
	if u'　' in u_str:
		return u_str.split(u'　')[-1]
	elif u' ' in u_str:
		return u_str.split(u' ')[-1]
	else:
		return u_str

def excel_to_json(genre, excel_file_path):
	filename = path.basename(excel_file_path)
	filename_without_ext, ext = path.splitext(excel_path)
	if ext != '.xls' and ext != '.xlsx':
		print 'extension has to be xls or xlsx'
		return
	
	wb = xlrd.open_workbook(excel_file_path,formatting_info=True,on_demand=True)
	#print 'Number of Sheets ', len(wb.sheets())
	# 一つ目のシートだけをパース対象とする
	sheet = wb.sheet_by_index(0)

	# 文書の最大の列、行の数を求める
	max_col_idx = sheet.ncols
	max_row_idx = sheet.nrows
	# 出力されるjsonデータ
	json_data = {'data':[]}

	# 解析を始める行
	start_row = 4

	if genre in ['rice','wheat','soybean']:
		json_data['goods'] = rm_unneed_char(sheet.cell(0,0).value)
		json_data['report_genre'] = crop_report_genre(sheet.cell(1,0).value),
		json_data['extraInfo'] = rm_unneed_char(sheet.cell(2,0).value)

		while sheet.cell(start_row, 0).value != u'全国':
			start_row += 1
			if start_row == max_row_idx:
				print "can't apply the algorism to this data"
				sys.exit(-1)

		# 重複している地域があるため、それを省く
		area_list = []
		for row_idx in range(start_row, max_row_idx):
			area = sheet.cell(row_idx, 0).value
			if area == '' or sheet.cell(row_idx, 1).value == '' or u'　' in sheet.cell(row_idx, 0).value:
				continue
			else:
				if genre in ['rice', 'wheat']:
					json_data['data'].append({	'area': area, 
												'areaUnderCultivation': {'value':sheet.cell(row_idx, 1).value,'unit':'ha'}, 
												'yield': {'value':sheet.cell(row_idx, 2).value, 'unit':'t'}
					})
				elif genre == 'soybean':
					json_data['data'].append({	'area': area,
												'areaUnderCultivation': {'value':sheet.cell(row_idx, 1).value,'unit':'ha'},
												'yield_per_10a': {'value':sheet.cell(row_idx, 2).value, 'unit':'kg'},
												'yield': {'value':sheet.cell(row_idx, 3).value, 'unit':'t'}
					})


	elif genre in ['fruits']:
		json_data['report_genre'] = crop_report_genre(sheet.cell(1,0).value),
		json_data['goods'] = rm_unneed_char(sheet.cell(3,0).value), 
		#json_data['extraInfo'] = sub_whitespace_number(sheet.cell(4,0).value),
		
		for row_idx in range(start_row, max_row_idx):
			read_col = 2
			# "全国"だけ異なる列にある
			if row_idx == start_row: read_col = 1
			area = sheet.cell(row_idx, read_col).value

			if area == '' or sheet.cell(row_idx, 4).value == '':
				continue
			else:
				json_data['data'].append({'area': area,
										'fruitingTreeArea': {'value':sheet.cell(row_idx, 4).value,'unit':'ha'},
										'yield_per_10a': {'value':sheet.cell(row_idx, 5).value, 'unit':'kg'},
										'yield': {'value':sheet.cell(row_idx, 6).value, 'unit':'t'},
										'shipment': {'value':sheet.cell(row_idx, 7).value, 'unit': 't'}
				})


	
	json_file_path = path.join(path.dirname(excel_file_path), filename_without_ext + '.json')
	#print json.dumps(json_data, ensure_ascii=False)
	with codecs.open(json_file_path, 'w', 'utf-8') as json_file:
		json.dump(json_data, json_file, indent=2, sort_keys=True, ensure_ascii=False)

if __name__ == '__main__':
	args_len = len(sys.argv) 
	if args_len != 3:
		print 'usage: python parse_excel.py genre excel_path'
		print 'genre: rice, wheat, soybean, fruits'
	else:
		genre = sys.argv[1]
		excel_path = sys.argv[2]
		excel_to_json(genre, excel_path)


