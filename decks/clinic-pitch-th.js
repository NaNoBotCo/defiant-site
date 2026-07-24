const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.layout = "LAYOUT_WIDE";           // 13.3 x 7.5
p.author = "Defiant";
p.title = "Defiant — Clinic Partnership Pitch (TH)";

const INDIGO = "1A1140", MAG = "E6197E", TEAL = "127D8B", TEAL2 = "16B5B5",
      WHITE = "FFFFFF", LIGHT = "F4F3F9", INK = "1A1140", MUTED = "6B6786",
      CARD = "FFFFFF";
const TH = "Tahoma";

function shadow() { return { type: "outer", color: "9C99B8", blur: 9, offset: 3, angle: 90, opacity: 0.35 }; }
function bg(s, c) { s.background = { color: c }; }
function rrect(s, x, y, w, h, fill, opts = {}) {
  s.addShape(p.ShapeType.roundRect, Object.assign({ x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { type: "none" }, shadow: shadow() }, opts));
}
function circle(s, x, y, d, fill) {
  s.addShape(p.ShapeType.ellipse, { x, y, w: d, h: d, fill: { color: fill }, line: { type: "none" } });
}
function kicker(s, text, color, x = 0.9, y = 0.62) {
  s.addText(text.toUpperCase(), { x, y, w: 8, h: 0.4, fontFace: TH, fontSize: 12, bold: true, color, charSpacing: 2, margin: 0 });
}

// ---------------------------------------------------------------- 1. COVER
let s = p.addSlide(); bg(s, INDIGO);
circle(s, 11.0, -1.6, 4.4, "241A5C");
circle(s, 12.2, 5.2, 3.2, "241A5C");
s.addText("DEFIANT", { x: 0.9, y: 0.7, w: 6, h: 0.6, fontFace: TH, fontSize: 24, bold: true, color: WHITE, charSpacing: 3, margin: 0 });
s.addShape(p.ShapeType.rect, { x: 0.92, y: 1.28, w: 0.7, h: 0.09, fill: { color: MAG }, line: { type: "none" } });
s.addText("ร่วมเป็นคลินิกพันธมิตรกับเรา", { x: 0.9, y: 2.15, w: 11.2, h: 1.5, fontFace: TH, fontSize: 46, bold: true, color: WHITE, margin: 0 });
s.addText("เราพาคนไข้ชาวอเมริกันและต่างชาติ มารักษาที่คลินิกของท่าน", { x: 0.9, y: 3.75, w: 10.8, h: 0.8, fontFace: TH, fontSize: 22, color: "D9D5F0", margin: 0 });
s.addText([
  { text: "ฟรี", options: { color: TEAL2, bold: true } },
  { text: "   ·   ไม่มีข้อผูกมัด   ·   เชียงใหม่", options: { color: "B7B2DA" } },
], { x: 0.9, y: 4.65, w: 10, h: 0.6, fontFace: TH, fontSize: 20, margin: 0 });
s.addText("Partner Clinics  ·  Defiant Health Concierge, Chiang Mai", { x: 0.9, y: 6.35, w: 9, h: 0.4, fontFace: TH, fontSize: 13, italic: true, color: "9A95C4", margin: 0 });
s.addText("LINE:  defiant.to", { x: 9.6, y: 6.32, w: 2.8, h: 0.45, fontFace: TH, fontSize: 15, bold: true, color: WHITE, align: "right", margin: 0 });
s.addNotes("เปิดด้วยการไหว้และแนะนำตัวสุภาพ: \"สวัสดีค่ะ/ครับ เราคือทีม Defiant พาคนไข้ชาวต่างชาติมารักษาที่เชียงใหม่\" บอกว่าขอเวลาสั้น ๆ ไม่มีข้อผูกมัด แค่อยากมาทำความรู้จักและเล่าว่าเราช่วยคลินิกได้อย่างไร");

// ---------------------------------------------------------------- 2. WHO WE ARE
s = p.addSlide(); bg(s, LIGHT);
kicker(s, "เราคือใคร", MAG);
s.addText("ทีมที่พาคนไข้ต่างชาติมาหาท่าน", { x: 0.9, y: 1.05, w: 11.4, h: 0.9, fontFace: TH, fontSize: 34, bold: true, color: INK, margin: 0 });
s.addText([
  { text: "เราคือ Defiant ", options: { bold: true, color: INK } },
  { text: "ทีมประสานงานด้านสุขภาพที่เชียงใหม่ เราพาคนไข้ชาวอเมริกันและชาวต่างชาติมารักษาที่เมืองไทย และดูแลให้ทุกขั้นตอน — นัดหมาย เอกสาร ล่าม และติดตามผล", options: { color: "3A3358" } },
], { x: 0.9, y: 2.25, w: 6.7, h: 2.6, fontFace: TH, fontSize: 20, lineSpacingMultiple: 1.3, valign: "top", margin: 0 });
rrect(s, 8.1, 2.15, 4.3, 3.4, INDIGO);
s.addText("โอกาสของท่าน", { x: 8.5, y: 2.5, w: 3.6, h: 0.5, fontFace: TH, fontSize: 17, bold: true, color: TEAL2, margin: 0 });
s.addText("คนไข้ต่างชาติจ่ายจริง และเป็นลูกค้าชั้นดี — แต่เข้าถึงยากเพราะภาษาและความเชื่อใจ", { x: 8.5, y: 3.15, w: 3.55, h: 1.6, fontFace: TH, fontSize: 19, color: WHITE, lineSpacingMultiple: 1.25, valign: "top", margin: 0 });
s.addText("เราเชื่อมให้ท่านเอง", { x: 8.5, y: 4.75, w: 3.55, h: 0.6, fontFace: TH, fontSize: 20, bold: true, color: MAG, margin: 0 });
s.addNotes("อธิบายว่าเราดูแลคนไข้ให้ครบทุกขั้นตอน — นัดหมาย เอกสาร ล่าม ติดตามผล. จุดสำคัญที่ต้องเน้น: คนไข้ต่างชาติจ่ายจริงและเป็นลูกค้าชั้นดี แต่คลินิกเข้าถึงยากเพราะภาษาและความเชื่อใจ — เราเป็นสะพานให้");

// ---------------------------------------------------------------- 3. WHAT YOU GET (2x2)
s = p.addSlide(); bg(s, WHITE);
kicker(s, "สิ่งที่ท่านจะได้รับ", MAG);
s.addText("เราดูแลให้หมด ท่านแค่รักษา", { x: 0.9, y: 1.05, w: 11.4, h: 0.9, fontFace: TH, fontSize: 34, bold: true, color: INK, margin: 0 });
const gets = [
  ["1", "คนไข้ที่คัดกรองแล้ว", "ส่งเฉพาะคนที่เหมาะกับบริการของท่าน ไม่รบกวนเวลาท่านเปล่า ๆ", MAG],
  ["2", "ลงประกาศคลินิกฟรี", "หน้าโปรไฟล์ภาษาอังกฤษบนเว็บของเรา ใช้เฉพาะข้อมูลที่ท่านอนุมัติ", TEAL],
  ["3", "มีล่ามไปทุกนัด", "ไทย ↔ อังกฤษ ท่านไม่ต้องมีพนักงานพูดอังกฤษเลย", TEAL],
  ["4", "เราจัดการเอกสารให้", "นัดหมาย ประวัติ บิลภาษาอังกฤษ และการติดตามผล", MAG],
];
gets.forEach((g, i) => {
  const x = 0.9 + (i % 2) * 5.95, y = 2.35 + Math.floor(i / 2) * 2.3;
  rrect(s, x, y, 5.55, 2.0, LIGHT);
  circle(s, x + 0.35, y + 0.35, 0.75, g[3]);
  s.addText(g[0], { x: x + 0.35, y: y + 0.36, w: 0.75, h: 0.75, fontFace: TH, fontSize: 26, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
  s.addText(g[1], { x: x + 1.35, y: y + 0.3, w: 4.0, h: 0.55, fontFace: TH, fontSize: 20, bold: true, color: INK, margin: 0 });
  s.addText(g[2], { x: x + 1.35, y: y + 0.85, w: 4.05, h: 1.0, fontFace: TH, fontSize: 15, color: "554F72", lineSpacingMultiple: 1.15, valign: "top", margin: 0 });
});
s.addNotes("ไล่ทีละข้อ. เน้นสองคำที่คลินิกชอบที่สุด: \"ฟรี\" และ \"มีล่ามให้ทุกนัด\". ย้ำว่าคลินิกไม่ต้องมีพนักงานพูดอังกฤษเลย ทุกอย่างเราจัดการให้");

// ---------------------------------------------------------------- 4. WHY GOOD BUSINESS
s = p.addSlide(); bg(s, LIGHT);
kicker(s, "ทำไมคนไข้ต่างชาติดีต่อธุรกิจ", MAG);
s.addText("ลูกค้าที่จ่ายจริง และกลับมาซ้ำ", { x: 0.9, y: 1.05, w: 11.4, h: 0.9, fontFace: TH, fontSize: 34, bold: true, color: INK, margin: 0 });
const why = [
  ["จ่ายเต็ม เงินสด", "ราคาไทยยังถูกกว่าบ้านเขา 50–80% เขายินดีจ่ายด้วยความเต็มใจ"],
  ["รัฐบาลสหรัฐจ่ายให้", "ทหารผ่านศึกอเมริกันเบิกค่ารักษาได้ (VA) — ผู้จ่ายที่เชื่อถือได้"],
  ["ประกัน / FSA / HSA", "คนไข้หลายคนเบิกได้ เราจัดบิลภาษาอังกฤษให้พร้อม"],
  ["ชื่อเสียงระดับสากล", "รีวิวจากคนไข้ต่างชาติ ช่วยให้คลินิกของท่านเป็นที่รู้จักมากขึ้น"],
];
why.forEach((wq, i) => {
  const x = 0.9 + i * 2.98;
  rrect(s, x, 2.5, 2.75, 3.4, CARD);
  s.addShape(p.ShapeType.rect, { x: x + 0.35, y: 2.9, w: 0.55, h: 0.09, fill: { color: i % 2 ? TEAL : MAG }, line: { type: "none" } });
  s.addText(wq[0], { x: x + 0.32, y: 3.15, w: 2.15, h: 1.0, fontFace: TH, fontSize: 20, bold: true, color: INK, valign: "top", margin: 0 });
  s.addText(wq[1], { x: x + 0.32, y: 4.15, w: 2.18, h: 1.55, fontFace: TH, fontSize: 14.5, color: "554F72", lineSpacingMultiple: 1.2, valign: "top", margin: 0 });
});
s.addNotes("กรอบความคิดสำคัญที่สุดของการพิตช์: นี่คือ \"ธุรกิจที่ดีสำหรับคลินิก\" ไม่ใช่การขอความช่วยเหลือ. คนไข้จ่ายเต็มเงินสด ราคาไทยถูกกว่าบ้านเขา 50–80% เขายินดีจ่าย. เกริ่นเรื่องทหารผ่านศึก (VA) ทิ้งท้ายเพื่อเข้าสไลด์ถัดไป");

// ---------------------------------------------------------------- 5. VA FMP (dark, centerpiece)
s = p.addSlide(); bg(s, INDIGO);
circle(s, -1.4, 4.6, 3.6, "241A5C");
kicker(s, "จุดเด่นที่ไม่มีใครเหมือน", TEAL2);
s.addText("VA FMP — ผู้จ่ายที่รัฐบาลสหรัฐรับรอง", { x: 0.9, y: 1.05, w: 11.4, h: 0.9, fontFace: TH, fontSize: 33, bold: true, color: WHITE, margin: 0 });
s.addText([
  { text: "ทหารผ่านศึกอเมริกันจำนวนมากอาศัยและมารักษาในไทย ", options: { color: "D9D5F0" }, breakLine: true },
  { text: "รัฐบาลสหรัฐจ่ายค่ารักษาคืน", options: { color: WHITE, bold: true } },
  { text: "ผ่านโครงการ Foreign Medical Program (FMP)", options: { color: "D9D5F0" } },
], { x: 0.9, y: 2.35, w: 6.7, h: 2.2, fontFace: TH, fontSize: 21, lineSpacingMultiple: 1.35, valign: "top", margin: 0 });
s.addText([
  { text: "คลินิกที่ทำเอกสาร FMP เป็น ", options: { color: TEAL2, bold: true }, breakLine: true },
  { text: "= ได้คนไข้กลุ่มนี้ที่เอกสารครบ และจ่ายแน่นอน", options: { color: WHITE } },
], { x: 0.9, y: 4.55, w: 6.7, h: 1.4, fontFace: TH, fontSize: 21, lineSpacingMultiple: 1.3, valign: "top", margin: 0 });
rrect(s, 8.15, 2.35, 4.25, 3.55, MAG);
s.addText("ผู้จ่าย =", { x: 8.5, y: 2.9, w: 3.6, h: 0.6, fontFace: TH, fontSize: 22, color: "FFD9EC", margin: 0 });
s.addText("รัฐบาลสหรัฐ", { x: 8.5, y: 3.5, w: 3.6, h: 1.0, fontFace: TH, fontSize: 34, bold: true, color: WHITE, margin: 0 });
s.addText("เชื่อถือได้ · จ่ายตรง · เอกสารครบ", { x: 8.5, y: 4.7, w: 3.6, h: 0.8, fontFace: TH, fontSize: 17, color: "FFE3F1", lineSpacingMultiple: 1.2, valign: "top", margin: 0 });
s.addNotes("จุดขายที่แข็งที่สุด — พูดช้า ๆ ให้เห็นภาพ. รัฐบาลสหรัฐจ่ายค่ารักษาคืนให้ทหารผ่านศึก (โครงการ FMP). คลินิกที่ทำเอกสาร FMP เป็น จะได้คนไข้กลุ่มนี้ที่เอกสารครบและจ่ายแน่นอน. ถามคลินิกตรง ๆ: \"เคยรับคนไข้ทหารผ่านศึกอเมริกันไหมคะ?\" ถ้าเขาสนใจ เรื่องเอกสารเราช่วยได้หมด");

// ---------------------------------------------------------------- 6. DTV / PAPERWORK (light + dark callout)
s = p.addSlide(); bg(s, LIGHT);
kicker(s, "โอกาสจากวีซ่า DTV", MAG);
s.addText("คนไข้อยู่ยาว จ่ายจริง — แต่ติดที่เอกสาร", { x: 0.9, y: 1.05, w: 11.4, h: 0.9, fontFace: TH, fontSize: 32, bold: true, color: INK, margin: 0 });
s.addText("คนไข้ต่างชาติอยากใช้ วีซ่า DTV รักษาระยะยาว (สูงสุด 180 วัน/ครั้ง) แต่หาคลินิกที่ทำเอกสารให้ถูกต้องไม่ได้:", { x: 0.9, y: 2.2, w: 6.7, h: 1.2, fontFace: TH, fontSize: 18, color: "3A3358", lineSpacingMultiple: 1.25, valign: "top", margin: 0 });
const dtvdocs = ["จดหมายเชิญจากคลินิก (มีตราประทับ)", "แผนการรักษาที่เซ็นและประทับตรา", "ใบอนุญาตคลินิก", "บิลภาษาอังกฤษ (เบิกประกัน / VA / FMP)"];
dtvdocs.forEach((d, i) => {
  const y = 3.55 + i * 0.62;
  circle(s, 0.98, y + 0.06, 0.2, i % 2 ? TEAL : MAG);
  s.addText(d, { x: 1.4, y: y - 0.06, w: 6.1, h: 0.5, fontFace: TH, fontSize: 16.5, color: INK, valign: "middle", margin: 0 });
});
rrect(s, 8.15, 2.2, 4.25, 3.75, INDIGO);
s.addText("คอขวด = เอกสาร", { x: 8.5, y: 2.6, w: 3.6, h: 0.5, fontFace: TH, fontSize: 18, color: "B7B2DA", margin: 0 });
s.addText("เราจัดการให้หมด", { x: 8.5, y: 3.15, w: 3.6, h: 0.9, fontFace: TH, fontSize: 30, bold: true, color: TEAL2, margin: 0 });
s.addText("ท่านแค่รักษา — เราดูแลเอกสารและวีซ่าให้เอง", { x: 8.5, y: 4.15, w: 3.6, h: 1.0, fontFace: TH, fontSize: 18, color: WHITE, lineSpacingMultiple: 1.2, valign: "top", margin: 0 });
s.addText("คนไข้อยู่ยาว = รายได้ต่อเนื่อง", { x: 8.5, y: 5.3, w: 3.6, h: 0.6, fontFace: TH, fontSize: 16, bold: true, color: MAG, margin: 0 });
s.addNotes("วีซ่า DTV ให้คนไข้อยู่รักษาได้ถึง 180 วันต่อครั้ง = รายได้ต่อเนื่องก้อนใหญ่. แต่คนไข้ส่วนมากติดตรงหาคลินิกที่ทำเอกสารวีซ่าให้ถูกต้องไม่ได้. ถามคลินิก: \"เคยออกจดหมาย/เอกสารวีซ่าให้คนไข้ต่างชาติไหมคะ?\" ถ้ายุ่งยากหรือไม่เคย — นี่คือจุดที่เราช่วย เราทำเอกสารและบิลอังกฤษให้หมด ท่านแค่รักษา");

// ---------------------------------------------------------------- 7. HOW IT WORKS (5 steps)
s = p.addSlide(); bg(s, WHITE);
kicker(s, "ขั้นตอนง่าย ๆ", MAG);
s.addText("ร่วมงานกับเราอย่างไร", { x: 0.9, y: 1.05, w: 11.4, h: 0.9, fontFace: TH, fontSize: 34, bold: true, color: INK, margin: 0 });
const steps = [
  ["1", "ลงประกาศให้ฟรี", "เราทำหน้าคลินิกภาษาอังกฤษให้ท่าน"],
  ["2", "จับคู่คนไข้", "เราส่งคนไข้ที่เหมาะกับบริการของท่าน"],
  ["3", "ล่ามไปด้วย", "ล่าม + ผู้ประสานงานไปพร้อมคนไข้"],
  ["4", "ท่านรักษา", "ท่านดูแลคนไข้ตามปกติ"],
  ["5", "ค่าแนะนำ", "แล้วแต่ท่านเห็นสมควร โปร่งใส"],
];
const sw = 2.3, gap = 0.15, x0 = 0.72;
steps.forEach((st, i) => {
  const x = x0 + i * (sw + gap);
  rrect(s, x, 2.85, sw, 2.7, LIGHT);
  circle(s, x + sw / 2 - 0.45, 2.5, 0.9, i % 2 ? TEAL : MAG);
  s.addText(st[0], { x: x + sw / 2 - 0.45, y: 2.5, w: 0.9, h: 0.9, fontFace: TH, fontSize: 32, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
  s.addText(st[1], { x: x + 0.15, y: 3.7, w: sw - 0.3, h: 0.6, fontFace: TH, fontSize: 18, bold: true, color: INK, align: "center", margin: 0 });
  s.addText(st[2], { x: x + 0.15, y: 4.3, w: sw - 0.3, h: 1.1, fontFace: TH, fontSize: 14, color: "554F72", align: "center", lineSpacingMultiple: 1.15, valign: "top", margin: 0 });
});
s.addNotes("ไล่ 5 ขั้นตอนให้เห็นว่าง่ายและเริ่มได้ทันที. เน้นขั้นแรก \"ลงประกาศฟรี\" (ไม่ต้องทำอะไรเลย) และขั้นสุดท้าย \"ค่าแนะนำแล้วแต่ท่าน\" — ไม่กดดัน ตกลงกันทีหลังได้");

// ---------------------------------------------------------------- 8. WHAT IT COSTS: NOTHING
s = p.addSlide(); bg(s, LIGHT);
rrect(s, 1.4, 1.7, 10.5, 4.1, INDIGO);
s.addText("ค่าใช้จ่ายของท่าน?", { x: 2.0, y: 2.3, w: 9, h: 0.7, fontFace: TH, fontSize: 26, color: "D9D5F0", align: "center", margin: 0 });
s.addText("ไม่มีเลย", { x: 2.0, y: 3.0, w: 9.3, h: 1.3, fontFace: TH, fontSize: 68, bold: true, color: TEAL2, align: "center", margin: 0 });
s.addText("ลงประกาศฟรี · ไม่มีข้อผูกมัด · เริ่มลองก่อน หยุดเมื่อไหร่ก็ได้ · ค่าแนะนำแล้วแต่ท่านสะดวกใจ", { x: 2.0, y: 4.5, w: 9.3, h: 0.9, fontFace: TH, fontSize: 18, color: WHITE, align: "center", lineSpacingMultiple: 1.25, valign: "top", margin: 0 });
s.addNotes("ย้ำให้ชัดและช้า: เริ่มต้นไม่มีค่าใช้จ่ายเลย ไม่มีข้อผูกมัด ลองก่อนได้ หยุดเมื่อไหร่ก็ได้. ใช้สไลด์นี้ลดความกังวลของคลินิก — ความเสี่ยงของเขาคือศูนย์");

// ---------------------------------------------------------------- 9. SPECIALTIES
s = p.addSlide(); bg(s, WHITE);
kicker(s, "บริการที่เรากำลังหา", MAG);
s.addText("คนไข้ของเรากำลังมองหา", { x: 0.9, y: 1.05, w: 11.4, h: 0.9, fontFace: TH, fontSize: 34, bold: true, color: INK, margin: 0 });
const specs = ["สูตินรีเวช", "ความงาม & ผิวหนัง", "ชะลอวัย & เวลเนส", "ดูแลผู้สูงอายุ", "ฟื้นฟู & กายภาพบำบัด", "ทันตกรรม", "จักษุ", "กระดูก & ข้อ", "โรงพยาบาลที่ทำ FMP"];
specs.forEach((sp, i) => {
  const x = 0.9 + (i % 3) * 3.87, y = 2.4 + Math.floor(i / 3) * 1.35;
  rrect(s, x, y, 3.6, 1.05, LIGHT);
  circle(s, x + 0.42, y + 0.42, 0.22, i % 2 ? TEAL : MAG);
  s.addText(sp, { x: x + 0.85, y: y, w: 2.65, h: 1.05, fontFace: TH, fontSize: 17, bold: true, color: INK, valign: "middle", margin: 0 });
});
s.addNotes("เปลี่ยนเป็นบทสนทนา: ถามว่าคลินิกเชี่ยวชาญด้านไหน แล้วชี้ให้เห็นว่าตรงกับที่คนไข้เรากำลังหา. ถ้าเขาทำ FMP/รับผู้สูงอายุได้ ยิ่งดี — เน้นตรงนั้น");

// ---------------------------------------------------------------- 10. NEXT STEPS / CONTACT (dark close)
s = p.addSlide(); bg(s, INDIGO);
circle(s, 10.6, -1.8, 4.6, "241A5C");
kicker(s, "มาเริ่มกันเลย", TEAL2);
s.addText("ขอบคุณที่สละเวลาค่ะ", { x: 0.9, y: 1.05, w: 11.4, h: 1.0, fontFace: TH, fontSize: 38, bold: true, color: WHITE, margin: 0 });
const nexts = [["1", "ทักไลน์มาหาเรา"], ["2", "เราคุยรายละเอียดกับท่าน"], ["3", "เราลงประกาศให้ฟรี"]];
nexts.forEach((n, i) => {
  const y = 2.55 + i * 0.95;
  circle(s, 0.95, y, 0.62, MAG);
  s.addText(n[0], { x: 0.95, y: y, w: 0.62, h: 0.62, fontFace: TH, fontSize: 22, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
  s.addText(n[1], { x: 1.8, y: y - 0.02, w: 6, h: 0.66, fontFace: TH, fontSize: 22, color: WHITE, valign: "middle", margin: 0 });
});
rrect(s, 8.1, 2.5, 4.3, 3.0, "241A5C", { shadow: { type: "outer", color: "0E0828", blur: 10, offset: 3, angle: 90, opacity: 0.5 } });
s.addText("ติดต่อเรา", { x: 8.45, y: 2.85, w: 3.6, h: 0.5, fontFace: TH, fontSize: 16, bold: true, color: TEAL2, margin: 0 });
s.addText("LINE ID", { x: 8.45, y: 3.5, w: 3.6, h: 0.4, fontFace: TH, fontSize: 15, color: "B7B2DA", margin: 0 });
s.addText("defiant.to", { x: 8.45, y: 3.85, w: 3.6, h: 0.7, fontFace: TH, fontSize: 30, bold: true, color: WHITE, margin: 0 });
s.addText("defiant.to/partners", { x: 8.45, y: 4.75, w: 3.6, h: 0.5, fontFace: TH, fontSize: 16, color: "D9D5F0", margin: 0 });
s.addNotes("ปิดด้วยขั้นตอนต่อไปที่ง่ายมาก: ขอเพิ่มไลน์ (ID: defiant.to) หรือให้คลินิกสแกน QR. เชิญให้ทักมาคุยรายละเอียดต่อ ทิ้งเอกสาร/PDF ไว้ให้. กล่าวขอบคุณที่สละเวลาอย่างสุภาพ ไหว้ลา");

p.writeFile({ fileName: "/private/tmp/claude-501/-Users-annikapeacock-Desktop-catalog/8ea10e00-bab2-41cc-b05d-113747077642/scratchpad/defiant-clinic-pitch.pptx" })
  .then(f => console.log("WROTE", f));
