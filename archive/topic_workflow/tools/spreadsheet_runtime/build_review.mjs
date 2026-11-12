import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const v2 = process.argv.includes('--v2');
const outputDir = path.join(root, v2 ? 'outputs/annotation_20261108_v2' : 'outputs/annotation_20261108');
await fs.mkdir(outputDir, {recursive:true});
const input = JSON.parse(await fs.readFile(path.join(root,v2 ? 'reports/annotation_review_v2.json' : 'reports/annotation_review.json'),'utf8'));
const wb = Workbook.create();
const sheets = [];
const sheetConfigs = v2 ? [['Duyet nhan','keep','ContractGuard — Nhãn sơ bộ sau xử lý nguồn']] : [
  ['Duyet nhan','keep','ContractGuard — Nhãn sơ bộ để bạn xác nhận'],
  ['De xuat loai','exclude','ContractGuard — Các đoạn đề xuất loại']
];
for (const [sheetName, action, title] of sheetConfigs) {
  const records = input.rows.filter(r=>r.proposed_action===action);
  const sheet = wb.worksheets.add(sheetName);
  sheet.showGridLines = false;
  sheet.tabColor = action==='keep' ? '#243C5A' : '#757575';
  const start = 9, last = start+records.length-1;
  const used = sheet.getRange(`A1:I${last}`);
  used.format.font = {name:'Arial', size:11, color:'#202B3C'};
  used.format.verticalAlignment = 'top';
  sheet.getRange('A2').values = [[title]];
  sheet.getRange('A2').format.font = {size:16, bold:true};
  sheet.getRange('A2:I2').format.rowHeight = 30;
  sheet.getRange('A3').values = [[action==='keep'
    ? 'Chỉ chọn Đạt hoặc Chưa đạt ở cột A. Tôi sẽ sửa nhãn khi bạn đánh dấu Chưa đạt.'
    : 'Chọn Đạt nếu đồng ý loại đoạn này. Chưa đạt: tôi sẽ trích/sửa nhãn lại.']];
  sheet.getRange('A4').values = [['Nhãn do Codex đề xuất cục bộ bằng quy tắc/ngữ cảnh, có hiệu chỉnh các trường hợp đã rà soát. Chưa được bạn phê duyệt để huấn luyện.']];
  sheet.getRange('A3:I4').format.rowHeight = 21;
  sheet.getRange('A5:C5').values = [['Đạt','Chưa đạt','Chờ xác nhận']];
  sheet.getRange('A6:C6').formulas = [[`=COUNTIFS(A${start}:A${last},"Đạt")`,
    `=COUNTIFS(A${start}:A${last},"Chưa đạt")`,`=COUNTIFS(A${start}:A${last},"Chờ xác nhận")`]];
  sheet.getRange('A6:C6').setNumberFormat('#,##0');
  sheet.getRange('A6:C6').format.font = {bold:true, size:14};
  const headers = ['Bạn xác nhận','Mã điều khoản','Nhãn sơ bộ','Nội dung điều khoản','Lý do đề xuất','Ghi chú của bạn (tùy chọn)','Nguồn','Trang','Mã nhãn'];
  sheet.getRange('A8:I8').values = [headers];
  const values = records.map(r=>['Chờ xác nhận',r.clause_id,
    r.label ? input.label_names[r.label] : 'Không gán nhãn — đề xuất loại',
    r.text,r.annotation_reason,'',r.source_url,
    r.page_start===r.page_end ? Number(r.page_start) : `${r.page_start}–${r.page_end}`,
    r.label || '']);
  sheet.getRange(`A${start}:I${last}`).values = values;
  const table = sheet.tables.add(`A8:I${last}`,true,action==='keep'?'LabelsForReview':'ProposedExclusions');
  table.showBandedRows = false;
  table.showFilterButton = true;
  sheet.getRange('A8:I8').format = {fill:'#243C5A',font:{color:'#FFFFFF',bold:true,name:'Arial',size:11},
    wrapText:true,verticalAlignment:'center',horizontalAlignment:'center',rowHeight:32};
  const widths = {A:145,B:255,C:235,D:690,E:440,F:300,G:500,H:90,I:140};
  for (const [column,width] of Object.entries(widths)) {
    sheet.getRange(`${column}8:${column}${last}`).format.columnWidthPx = width;
  }
  sheet.getRange(`A${start}:I${last}`).format.wrapText = true;
  sheet.getRange(`A${start}:A${last}`).format.fill = '#FFF2CD';
  sheet.getRange(`F${start}:F${last}`).format.fill = '#FFF9E9';
  sheet.getRange(`A${start}:A${last}`).dataValidation = {
    rule:{type:'list',values:['Chờ xác nhận','Đạt','Chưa đạt']}};
  sheet.getRange(`A${start}:A${last}`).conditionalFormats.add('containsText',{
    text:'Chưa đạt',format:{fill:'#FCE4DF',font:{color:'#A3261F',bold:true}}});
  for (let i=0;i<records.length;i++) {
    const r = records[i];
    const lines = Math.max(Math.ceil(r.text.length/83),Math.ceil(r.annotation_reason.length/53),3);
    sheet.getRange(`A${start+i}:I${start+i}`).format.rowHeight = Math.min(409,lines*15+15);
  }
  sheet.freezePanes.freezeRows(8);
  sheet.freezePanes.freezeColumns(3);
  sheets.push({name:sheetName,records,first:start,last});
}
wb.recalculate();
// Validate review counts and input behavior without retaining a simulated decision.
for (const item of sheets) {
  const sheet = wb.worksheets.getItem(item.name);
  let counts = sheet.getRange('A6:C6').values[0];
  if (counts[0]!==0 || counts[1]!==0 || counts[2]!==item.records.length) throw Error('Initial review counts are incorrect');
  sheet.getRange('A9').values = [['Đạt']];
  wb.recalculate();
  counts = sheet.getRange('A6:C6').values[0];
  if (counts[0]!==1 || counts[2]!==item.records.length-1) throw Error('Review counts did not react to input');
  sheet.getRange('A9').values = [['Chờ xác nhận']];
}
wb.recalculate();
const errors = await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',
  options:{useRegex:true,maxResults:20},maxChars:1500});
await fs.writeFile(path.join(outputDir,'workbook_check.json'),JSON.stringify({summary:input.summary,
  formulaErrorScan:errors.ndjson,reviewInputRecalculationVerified:true},null,2));
for (const item of sheets) {
  const preview = await wb.render({sheetName:item.name,range:'A2:E12',scale:1,format:'png'});
  await fs.writeFile(path.join(outputDir,item.name.replaceAll(' ','_')+'.png'),new Uint8Array(await preview.arrayBuffer()));
}
const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(path.join(outputDir,'ContractGuard_DuyetNhan.xlsx'));
console.log(JSON.stringify({path:path.join(outputDir,'ContractGuard_DuyetNhan.xlsx'),
  sheets:sheets.map(x=>({name:x.name,rows:x.records.length})),summary:input.summary}));
