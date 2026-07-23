#!/usr/bin/env python3
"""Content database for the Defiant directory — procedures, hospitals, destinations.

Single-purpose: gen_vault_notes.py reads these dicts and writes Obsidian notes
into the vault at ~/Documents/Defiant. After generation THE VAULT IS CANONICAL;
this file is provenance + regeneration seed only (regeneration never overwrites
an existing note).

All price bands are indicative 2026 USD ranges drawn from published medical-
tourism aggregators and hospital price lists (Bookimed, Medical Departures,
hospital published rates). They are deliberately ranges, marked indicative on
every page, and live inside machine-refresh blocks so a future crawler can
update them without touching hand-written prose.
"""

# ---------------------------------------------------------------- procedures
# key = exact wikilink name used in "Public Links/=Procedures.md" (must match!)
PROCEDURES = {
    # ---- Orthopedic
    "Hip Replacement": dict(
        cat="Orthopedic", us="$30,000–$50,000", th="$11,000–$17,000",
        stay="10–14 nights in-country, walking day 1–2, fly home ~day 12",
        hosps=["Bumrungrad International Hospital", "Bangkok Hospital", "Vejthani Hospital", "Bangkok Hospital Chiang Mai", "Sriphat Medical Center"],
        blurb=(
            "Total hip arthroplasty is the single most classic medical-tourism procedure: mature "
            "technique, predictable recovery, and a US price tag that has nothing to do with the "
            "cost of the implant. Thai private hospitals run high-volume joint centers with the "
            "same implant brands used in the US (Zimmer Biomet, Stryker, DePuy), and physical "
            "therapy is included in most packages rather than billed as a surprise."),
        notes="Ask for the surgeon's annual joint volume and which implant line is quoted — both belong in writing before you fly."),
    "Knee Replacement": dict(
        cat="Orthopedic", us="$30,000–$50,000", th="$10,000–$16,000",
        stay="10–14 nights, PT starts day 1",
        hosps=["Bumrungrad International Hospital", "Vejthani Hospital", "Bangkok Hospital", "Bangkok Hospital Chiang Mai", "Sriphat Medical Center"],
        blurb=(
            "Total and partial knee replacement at Thai joint centers, including robotic-assisted "
            "options at the Bangkok flagships. Packages typically bundle the implant, theatre, "
            "5–7 hospital nights and initial physiotherapy — the line items US hospitals unbundle."),
        notes="Bilateral (both knees, one trip) is commonly offered; it saves a second airfare but doubles early rehab intensity — a real intake conversation, not a brochure checkbox."),
    "Shoulder Replacement": dict(
        cat="Orthopedic", us="$25,000–$45,000", th="$10,000–$15,000",
        stay="7–12 nights, sling 4–6 weeks",
        hosps=["Bumrungrad International Hospital", "Bangkok Hospital", "Vejthani Hospital"],
        blurb=(
            "Anatomic and reverse shoulder arthroplasty for arthritis and irreparable cuff tears. "
            "Fewer surgeons do this well than hips and knees — anywhere on earth — so the shortlist "
            "matters more than the discount."),
        notes="Physical therapy continues months after you fly home; we help line up the hand-off plan before surgery."),
    "Spinal Surgery": dict(
        cat="Orthopedic", us="$50,000–$150,000", th="$15,000–$40,000",
        stay="10–21 nights depending on levels fused",
        hosps=["Bumrungrad International Hospital", "Bangkok Hospital", "MedPark Hospital", "Vejthani Hospital"],
        blurb=(
            "Fusion, decompression, and disc replacement at spine centers with intraoperative "
            "navigation and neuromonitoring. The US price spread on spine work is the widest in "
            "medicine; the Thai spread is merely wide. Second opinions are cheap here — get one "
            "before anyone fuses anything."),
        notes="We insist on imaging review before travel: send your MRI, get the surgical plan and quote in writing, then buy the ticket."),
    "Arthroscopy": dict(
        cat="Orthopedic", us="$8,000–$20,000", th="$3,000–$7,000",
        stay="3–7 nights, crutches optional",
        hosps=["Bangkok Hospital Chiang Mai", "Chiang Mai Ram Hospital", "Bumrungrad International Hospital", "Vejthani Hospital"],
        blurb=(
            "Keyhole repair for meniscus, labrum, ACL and rotator-cuff work. Small enough to pair "
            "with a recovery holiday, big enough to bankrupt you at US ambulatory-center rates."),
        notes="ACL reconstruction packages in Chiang Mai routinely come in under a US facility fee alone."),

    # ---- Cardiovascular
    "Heart Bypass Surgery (CABG)": dict(
        cat="Cardiovascular", us="$70,000–$200,000", th="$15,000–$35,000",
        stay="14–21 nights, cleared to fly after surgical review",
        hosps=["Bangkok Hospital", "Bumrungrad International Hospital", "MedPark Hospital", "Praram 9 Hospital"],
        blurb=(
            "Coronary artery bypass grafting at dedicated cardiac institutes — Bangkok Hospital's "
            "Heart Institute and Bumrungrad's cardiac center run volumes comparable to major US "
            "programs, with published outcome data on request. This is the procedure where the "
            "80% saving stops being abstract and becomes a retirement you still get to have."),
        notes="Cardiac work is where you bring the full file: angiogram, echo, med list. We coordinate records before any quote is treated as real."),
    "Heart Valve Replacement": dict(
        cat="Cardiovascular", us="$80,000–$200,000", th="$18,000–$40,000",
        stay="14–21 nights",
        hosps=["Bangkok Hospital", "Bumrungrad International Hospital", "MedPark Hospital"],
        blurb=(
            "Open and transcatheter (TAVI/TAVR) valve programs with US- and EU-trained interventional "
            "teams. TAVI availability at Thai flagships has grown fast — often with shorter waits "
            "than the US pre-authorization gauntlet."),
        notes="Mechanical vs tissue valve is a lifestyle decision (anticoagulation forever vs re-operation someday) — decide it with a cardiologist, not a price list."),
    "Angioplasty and Stenting": dict(
        cat="Cardiovascular", us="$25,000–$60,000", th="$8,000–$18,000",
        stay="4–7 nights",
        hosps=["Bangkok Hospital", "Praram 9 Hospital", "Bumrungrad International Hospital", "Bangkok Hospital Chiang Mai"],
        blurb=(
            "PCI with drug-eluting stents, same manufacturers as US cath labs. For stable disease "
            "this is a planned, packaged procedure in Thailand rather than a five-figure surprise."),
        notes="Not for emergencies — if you're having a heart attack, go to the nearest hospital wherever you are. This page is for the scheduled kind."),
    "Pacemaker Implantation": dict(
        cat="Cardiovascular", us="$20,000–$50,000", th="$8,000–$15,000",
        stay="4–7 nights",
        hosps=["Bangkok Hospital", "Bumrungrad International Hospital", "MedPark Hospital"],
        blurb=(
            "Single/dual-chamber and leadless devices from the usual global makers (Medtronic, "
            "Abbott, Boston Scientific). Device cost is the bulk of the bill; Thai hospitals quote "
            "it as one number instead of a claims mystery."),
        notes="Plan device follow-up before you fly home — most US cardiology practices will interrogate any standard device; we get it confirmed in writing."),

    # ---- Cosmetic & Aesthetic
    "Breast Augmentation": dict(
        cat="Cosmetic & Aesthetic", us="$8,000–$12,000", th="$3,000–$5,500",
        stay="7–10 nights, no lifting 2 weeks",
        hosps=["Yanhee International Hospital", "Samitivej Sukhumvit Hospital", "Preecha Aesthetic Institute", "Chiang Mai Ram Hospital"],
        blurb=(
            "Implant and fat-transfer augmentation in accredited hospitals — not strip-mall clinics. "
            "Thailand's cosmetic surgery volume means your surgeon has likely done this week what a "
            "US suburban surgeon does in a quarter."),
        notes="Implant brand and warranty card in writing (Mentor and Motiva are standard here); revision policy stated before deposit."),
    "Breast Reduction": dict(
        cat="Cosmetic & Aesthetic", us="$8,000–$15,000", th="$3,500–$6,000",
        stay="7–12 nights",
        hosps=["Yanhee International Hospital", "Samitivej Sukhumvit Hospital", "Preecha Aesthetic Institute"],
        blurb=(
            "One of the highest patient-satisfaction procedures in all of surgery, and one US "
            "insurers love to deny as 'cosmetic'. In Thailand it's simply a scheduled operation "
            "with a flat price."),
        notes="Bring your denial letter if you have one. Frame it. Then come get the surgery for less than your deductible."),
    "Facelift": dict(
        cat="Cosmetic & Aesthetic", us="$12,000–$25,000", th="$4,000–$9,000",
        stay="10–14 nights, presentable at ~2 weeks",
        hosps=["Preecha Aesthetic Institute", "Yanhee International Hospital", "Kamol Cosmetic Hospital"],
        blurb=(
            "Deep-plane and SMAS facelifts by surgeons who do them daily. Recovery in a quiet Thai "
            "hotel beats recovery while hiding from your coworkers."),
        notes="The 10–14 day in-country window is non-negotiable: sutures out and surgeon review happen before you fly."),
    "Rhinoplasty (Nose Surgery)": dict(
        cat="Cosmetic & Aesthetic", us="$8,000–$15,000", th="$2,000–$5,000",
        stay="7–10 nights, splint off ~day 7",
        hosps=["Yanhee International Hospital", "Preecha Aesthetic Institute", "Kamol Cosmetic Hospital"],
        blurb=(
            "Cosmetic and functional (septum) rhinoplasty. Thai surgeons are regionally famous for "
            "both augmentation and reduction work — bring reference photos, leave with a plan, "
            "not a template nose."),
        notes="Revision rhinoplasty is a different, harder animal — say so at intake and we shortlist accordingly."),
    "Liposuction": dict(
        cat="Cosmetic & Aesthetic", us="$4,000–$10,000", th="$1,500–$4,000",
        stay="5–10 nights, compression garment 4–6 weeks",
        hosps=["Yanhee International Hospital", "Kamol Cosmetic Hospital", "Preecha Aesthetic Institute", "Chiang Mai Ram Hospital"],
        blurb=(
            "Tumescent and VASER lipo, priced per area in a way you can actually read. Multiple "
            "areas in one session is routine and quoted upfront."),
        notes="Lipo is contouring, not weight loss — if a clinic anywhere sells it as weight loss, walk."),
    "Abdominoplasty (Tummy Tuck)": dict(
        cat="Cosmetic & Aesthetic", us="$8,000–$15,000", th="$3,500–$6,500",
        stay="10–14 nights, no flying earlier",
        hosps=["Yanhee International Hospital", "Preecha Aesthetic Institute", "Samitivej Sukhumvit Hospital"],
        blurb=(
            "Full and mini abdominoplasty, often paired with lipo or hernia repair in one "
            "anesthesia. A real operation with a real recovery — plan the longer stay."),
        notes="Frequently combined with post-bariatric body work; if that's you, see Body Contouring too."),
    "Hair Transplant": dict(
        cat="Cosmetic & Aesthetic", us="$8,000–$15,000", th="$2,500–$6,000",
        stay="3–5 nights, hat weather after",
        hosps=["Yanhee International Hospital", "Bumrungrad International Hospital"],
        blurb=(
            "FUE and DHI by the graft, at per-graft prices a third of US rates. Bangkok competes "
            "with Istanbul on price while being a far better place to spend the week."),
        notes="Quote should state technique, graft count, and who actually does the extraction (surgeon vs tech team)."),
    "Botox and Fillers": dict(
        cat="Cosmetic & Aesthetic", us="$400–$1,500 per session", th="$150–$500 per session",
        stay="Same-day; pairs with any trip",
        hosps=["Yanhee International Hospital", "Samitivej Sukhumvit Hospital", "Chiang Mai Ram Hospital"],
        blurb=(
            "Injectables at hospital dermatology departments — genuine product, doctor-administered, "
            "receipts with batch numbers. The counterfeit-Botox problem is real worldwide; hospitals "
            "are the boring, correct answer."),
        notes="If you're already coming for something bigger, this is the classic add-on appointment."),

    # ---- Dental
    "Dental Implants": dict(
        cat="Dental", us="$3,000–$5,000 per tooth", th="$1,000–$1,800 per tooth",
        stay="Two trips (placement + crown) or One-trip immediate-load cases",
        hosps=["Bangkok International Dental Center", "Bangkok Hospital Chiang Mai", "Chiang Mai Ram Hospital"],
        blurb=(
            "Titanium implants (Straumann, Nobel Biocare, Osstem) placed by dental surgeons at a "
            "third of US chairside prices. Full-arch (All-on-4/6) cases are where five figures of "
            "savings appear — and where our founder's own story started: fixing overpriced US "
            "military dental work in Chiang Mai fifteen years ago."),
        notes="Standard implants need osseointegration time — two trips ~3–6 months apart. Anyone promising everything in 5 days for every case is selling airline tickets, not dentistry."),
    "Veneers": dict(
        cat="Dental", us="$1,000–$2,500 per tooth", th="$250–$550 per tooth",
        stay="5–8 nights, two visits",
        hosps=["Bangkok International Dental Center", "Bangkok Hospital Chiang Mai"],
        blurb=(
            "Porcelain (e.max, zirconia) veneers with in-house labs — the reason 'Thailand smile "
            "makeover' is a whole genre. A full visible-arch case still costs less than four teeth "
            "at home."),
        notes="Good veneers require grinding healthy enamel — irreversible. An honest dentist will talk some patients into whitening instead; that's a green flag."),
    "Crowns and Bridges": dict(
        cat="Dental", us="$1,000–$2,500 per unit", th="$300–$700 per unit",
        stay="4–7 nights",
        hosps=["Bangkok International Dental Center", "Bangkok Hospital Chiang Mai", "Chiang Mai Ram Hospital"],
        blurb=("Same-brand ceramics, in-house milling, days not weeks. Bread-and-butter work priced like it."),
        notes="Bring or request current X-rays so quotes are per-your-mouth, not per-brochure."),
    "Root Canal Treatment": dict(
        cat="Dental", us="$1,000–$2,000", th="$250–$600",
        stay="3–5 nights",
        hosps=["Bangkok International Dental Center", "Chiang Mai Ram Hospital"],
        blurb=("Endodontics by specialists with microscopes, at prices that don't make extraction tempting for the wrong reason."),
        notes="Usually needs a crown after — budget both lines from the start."),
    "Orthodontics (Braces, Aligners)": dict(
        cat="Dental", us="$4,000–$8,000", th="$1,500–$3,500",
        stay="Multi-visit over months — expat/long-stay play, not a fly-in",
        hosps=["Bangkok International Dental Center", "Chiang Mai Ram Hospital"],
        blurb=(
            "Braces and clear aligners priced for people who live here or visit often. For pure "
            "fly-in patients, aligner systems with remote monitoring can work — honest answer: "
            "orthodontics is the weakest fit for one-trip tourism on this whole list."),
        notes="If you're relocating anyway (see the expat services side of the house), this is a great local price."),

    # ---- Fertility & Reproductive
    "In Vitro Fertilization (IVF)": dict(
        cat="Fertility & Reproductive", us="$15,000–$25,000 per cycle", th="$8,000–$12,000 per cycle",
        stay="2–3 weeks per cycle, or split-trip protocols",
        hosps=["Jetanin Institute", "Superior A.R.T.", "Samitivej Sukhumvit Hospital", "Bumrungrad International Hospital"],
        blurb=(
            "Dedicated IVF institutes with published lab standards and genetic testing (PGT-A) "
            "in-house. Straight talk on Thai law: IVF here is available to legally married "
            "heterosexual couples — bring your marriage certificate; sex selection is prohibited. "
            "If that law excludes your family, tell us — routing patients to the right jurisdiction "
            "is exactly the kind of logistics we exist for."),
        notes="Thai law (2015 ART Act) is strict and enforced. Anyone waving those requirements away is a risk to your money and your embryos."),
    "Egg Freezing": dict(
        cat="Fertility & Reproductive", us="$10,000–$15,000 + storage", th="$3,500–$6,000 + storage",
        stay="~2 weeks (stimulation to retrieval)",
        hosps=["Jetanin Institute", "Superior A.R.T.", "Samitivej Sukhumvit Hospital"],
        blurb=(
            "Oocyte cryopreservation for single women is legal and available in Thailand — one of "
            "the cleaner legal paths in Thai fertility law. Annual storage runs a few hundred "
            "dollars, not a few thousand."),
        notes="Future use of frozen eggs in Thailand falls under the marriage requirement — many clients freeze here, transport later. We handle the shipping logistics conversation upfront."),
    "Surrogacy Services": dict(
        cat="Fertility & Reproductive", us="$120,000–$200,000 (US agencies)", th="Not available",
        stay="—",
        hosps=[],
        blurb=(
            "Honesty box, no sugar: **commercial surrogacy for foreigners is banned in Thailand** "
            "(2015 ART Act, passed after the Baby Gammy scandal). Anyone selling you Thai "
            "surrogacy today is selling you a crime scene. We keep this page up because people "
            "search for it and deserve a straight answer instead of a scam."),
        notes="Where clients go instead: US, Canada, Georgia, Mexico (each with its own law and risk profile). Book an intake call if you want the honest map — we'd rather route you right than book you at all."),
    "ICSI (Intracytoplasmic Sperm Injection)": dict(
        cat="Fertility & Reproductive", us="+$1,500–$3,000 on IVF", th="Often bundled; +$500–$1,000",
        stay="Same footprint as IVF",
        hosps=["Jetanin Institute", "Superior A.R.T.", "Bumrungrad International Hospital"],
        blurb=("Standard add-on for male-factor infertility; Thai institutes frequently bundle it where US clinics line-item it."),
        notes="Same legal frame as IVF — married heterosexual couples, certificate required."),

    # ---- Bariatric / Weight Loss
    "Gastric Bypass Surgery": dict(
        cat="Bariatric / Weight Loss", us="$20,000–$30,000", th="$12,000–$17,000",
        stay="10–14 nights, liquid diet phase in-country",
        hosps=["Yanhee International Hospital", "Bumrungrad International Hospital", "MedPark Hospital"],
        blurb=(
            "Roux-en-Y bypass at high-volume bariatric units with multidisciplinary teams "
            "(surgeon, dietitian, endocrinologist). US insurers demand months of documented "
            "'supervised diet' before approving; Thailand demands a workup and a date."),
        notes="Lifelong supplement protocol and follow-up labs — we make sure the aftercare plan lands with a provider back home before surgery."),
    "Sleeve Gastrectomy": dict(
        cat="Bariatric / Weight Loss", us="$15,000–$25,000", th="$9,000–$14,000",
        stay="8–12 nights",
        hosps=["Yanhee International Hospital", "Bumrungrad International Hospital", "MedPark Hospital"],
        blurb=(
            "The most-performed bariatric operation worldwide, packaged cleanly at Thai centers. "
            "Quotes include the stapler and consumables — the line items that ambush US bills."),
        notes="BMI and comorbidity criteria still apply; a center that operates on anyone with a credit card is a red flag anywhere on earth."),
    "Gastric Band Surgery": dict(
        cat="Bariatric / Weight Loss", us="$15,000–$20,000", th="$8,000–$12,000",
        stay="5–8 nights",
        hosps=["Yanhee International Hospital"],
        blurb=(
            "Honesty first: banding has fallen out of favor globally (revision and erosion rates); "
            "most centers now recommend sleeve or bypass. We list it because it's still asked for, "
            "and band *removal/revision* is its own growing category."),
        notes="If you have an old band causing trouble, revision surgery here costs less than the US removal alone."),

    # ---- Gender Affirmation
    "Top Surgery": dict(
        cat="Gender Affirmation", us="$8,000–$15,000", th="$3,000–$6,500",
        stay="10–14 nights",
        hosps=["Kamol Cosmetic Hospital", "Preecha Aesthetic Institute", "Yanhee International Hospital"],
        blurb=(
            "Masculinizing chest surgery and feminizing augmentation by surgeons for whom this is "
            "a primary practice, not an occasional sideline. Thailand has been doing gender-"
            "affirming surgery at volume for four decades — while US access gets legislated "
            "backwards, Bangkok's ORs just keep running."),
        notes="Standard requirements: hormone/readiness letters per WPATH-style criteria; we tell you the exact document list per surgeon at intake."),
    "Facial Feminization Surgery (FFS)": dict(
        cat="Gender Affirmation", us="$30,000–$70,000", th="$12,000–$28,000",
        stay="14–21 nights",
        hosps=["Kamol Cosmetic Hospital", "Preecha Aesthetic Institute"],
        blurb=(
            "Forehead, jaw, tracheal shave, rhinoplasty — staged or combined — from teams with "
            "some of the deepest FFS caseloads anywhere. US quotes for equivalent staged work "
            "regularly cross six figures; Bangkok's don't."),
        notes="FFS planning runs on CT imaging and surgeon aesthetics — video consult + imaging review before you commit to anything."),
    "Vaginoplasty": dict(
        cat="Gender Affirmation", us="$25,000–$60,000", th="$9,000–$22,000",
        stay="21–30 nights — this is the long stay on this list",
        hosps=["Suporn Clinic", "Kamol Cosmetic Hospital", "Preecha Aesthetic Institute", "Yanhee International Hospital"],
        blurb=(
            "Thailand is, without hyperbole, the global center of gravity for this surgery — "
            "techniques used worldwide were developed and refined here. Waitlists at the famous "
            "clinics are real (often 1–2 years); mid-tier hospital programs run shorter. The "
            "in-country recovery is long and structured: this is the procedure where concierge "
            "support earns its keep."),
        notes="Requirements are strict and non-negotiable at reputable clinics (age, RLE, letters, sometimes BMI). Dilation schedule dominates the first months — housing with privacy matters; we arrange it."),
    "Phalloplasty": dict(
        cat="Gender Affirmation", us="$50,000–$150,000", th="$25,000–$60,000",
        stay="30+ nights, often staged across trips",
        hosps=["Kamol Cosmetic Hospital", "Preecha Aesthetic Institute"],
        blurb=(
            "Fewer surgeons worldwide do phalloplasty well than any other procedure on this site. "
            "Thailand has credible programs (radial forearm and ALT flap techniques), typically "
            "staged. We will name the honest trade-offs per surgeon rather than pretend a "
            "directory page can decide this for you."),
        notes="Multi-stage by design (typically 2–3 trips). Complication management planning — who fixes what, where, covered how — goes in the contract, not in hope."),
    "Body Contouring": dict(
        cat="Gender Affirmation", us="$10,000–$30,000", th="$4,000–$12,000",
        stay="10–14 nights",
        hosps=["Kamol Cosmetic Hospital", "Yanhee International Hospital", "Preecha Aesthetic Institute"],
        blurb=(
            "Affirming silhouette work — hip/butt augmentation, waist contouring, post-massive-"
            "weight-loss skin surgery — quoted as one plan instead of a la carte confusion."),
        notes="Often combined with top surgery or FFS trips; combining under one anesthesia is a surgeon call, not a savings hack."),

    # ---- Ophthalmology
    "LASIK Eye Surgery": dict(
        cat="Ophthalmology", us="$2,000–$4,500 both eyes", th="$1,000–$2,000 both eyes",
        stay="4–6 nights, next-day check required",
        hosps=["Rutnin Eye Hospital", "Bumrungrad International Hospital"],
        blurb=(
            "LASIK/PRK/SMILE at dedicated eye hospitals with the current-generation lasers. "
            "Screening is the product — a good center disqualifies bad corneas; that's what "
            "you're paying for."),
        notes="No diving or pools for a couple of weeks — schedule the beach leg of the trip *before* surgery, not after."),
    "Cataract Surgery": dict(
        cat="Ophthalmology", us="$3,500–$7,000 per eye", th="$1,200–$2,500 per eye",
        stay="5–8 nights for one eye; both eyes = staged days apart",
        hosps=["Rutnin Eye Hospital", "Bangkok Hospital", "Bumrungrad International Hospital"],
        blurb=(
            "Phaco with monofocal through trifocal IOL options — the premium-lens upsell exists "
            "everywhere, but here even the premium lens costs less than a US basic package."),
        notes="Lens choice (mono/EDOF/trifocal) determines glasses-freedom and night-halo trade-offs; decide with the surgeon's biometry in front of you."),
    "Retinal Surgery": dict(
        cat="Ophthalmology", us="$10,000–$25,000", th="$4,000–$10,000",
        stay="10–14 nights; gas-bubble cases CANNOT fly until cleared",
        hosps=["Rutnin Eye Hospital", "Bangkok Hospital"],
        blurb=(
            "Vitrectomy and retinal-detachment repair at subspecialty centers. Detachment is "
            "urgent — this page is for planned vitreoretinal work, not emergencies."),
        notes="If your repair used a gas bubble, flying before clearance can blind the eye. The no-fly window is absolute and we schedule around it."),
    "Corneal Transplants": dict(
        cat="Ophthalmology", us="$15,000–$30,000", th="$6,000–$12,000",
        stay="14–21 nights initial; multiple follow-ups",
        hosps=["Rutnin Eye Hospital", "Bangkok Hospital"],
        blurb=(
            "PK and lamellar (DSAEK/DMEK) grafts. Honest constraint: donor tissue in Thailand "
            "flows through the Thai Red Cross eye bank and availability can set your timeline "
            "more than the surgeon's calendar does."),
        notes="Long steroid-drop protocols and rejection surveillance — the back-home ophthalmologist hand-off is part of our checklist, not an afterthought."),

    # ---- Oncology
    "Cancer Screenings": dict(
        cat="Oncology", us="$2,000–$5,000 full panel", th="$400–$1,200 full panel",
        stay="2–4 nights; results consult included",
        hosps=["Bumrungrad International Hospital", "Bangkok Hospital", "MedPark Hospital", "Bangkok Hospital Chiang Mai"],
        blurb=(
            "Executive-style screening panels — imaging, scopes, tumor markers, same-week results "
            "with a physician consult — for less than a US colonoscopy's facility fee. This is the "
            "lowest-friction first date with Thai healthcare: fly in skeptical, fly out with data."),
        notes="US-side follow-up for anything found is part of the plan we build — screening without a follow-up path is just expensive anxiety."),
    "Chemotherapy": dict(
        cat="Oncology", us="$10,000–$200,000+ course", th="$1,000–$5,000 per cycle typical",
        stay="Cycle-based; many clients relocate for treatment blocks",
        hosps=["Bangkok Hospital", "MedPark Hospital", "Bumrungrad International Hospital"],
        blurb=(
            "Systemic therapy — including current targeted and immunotherapy agents — administered "
            "at accredited cancer centers at drug prices US patients genuinely do not believe "
            "until they see the invoice. Some clients pair Thai treatment cycles with US "
            "oncologist oversight; we broker that arrangement explicitly."),
        notes="Oncology is never a price-shopping exercise alone: regimen equivalence gets confirmed between your US records and the Thai oncologist before anyone books anything."),
    "Radiation Therapy": dict(
        cat="Oncology", us="$30,000–$80,000 course", th="$8,000–$20,000 course",
        stay="Daily sessions over 3–7 weeks — a residency, not a trip",
        hosps=["Bangkok Hospital", "MedPark Hospital", "Bumrungrad International Hospital"],
        blurb=(
            "IMRT/VMAT and stereotactic programs on current linear accelerators. The multi-week "
            "daily schedule makes this a temporary relocation — which is exactly the logistics "
            "problem a Chiang Mai/Bangkok concierge exists to solve: housing near the machine, "
            "not near the brochure."),
        notes="Proton therapy exists in Thailand (Chulabhorn, Bangkok) with limited slots — ask at intake if your case indicates it."),
    "Surgical Oncology": dict(
        cat="Oncology", us="$40,000–$150,000+", th="$10,000–$40,000",
        stay="Case-dependent; plan 2–4 weeks",
        hosps=["MedPark Hospital", "Bangkok Hospital", "Bumrungrad International Hospital"],
        blurb=(
            "Tumor resections with modern staging, frozen-section pathology, and MDT (tumor "
            "board) review. For solid tumors where surgery is the curative step, the US pricing "
            "delta is life-changing money at exactly the moment you need it least."),
        notes="We coordinate pathology slide/block transfer both directions — continuity of the specimen record is non-negotiable in cancer care."),

    # ---- General Surgery
    "Gallbladder Removal (Cholecystectomy)": dict(
        cat="General Surgery", us="$12,000–$20,000", th="$4,000–$7,000",
        stay="5–8 nights",
        hosps=["Bangkok Hospital Chiang Mai", "Chiang Mai Ram Hospital", "Bumrungrad International Hospital"],
        blurb=("Laparoscopic gallbladder removal — one of the most standardized operations in existence, priced accordingly here and mysteriously not in the US."),
        notes="If you're having active attacks, don't wait for a flight window that suits the fare calendar — gallbladders don't read fare calendars."),
    "Hernia Repair": dict(
        cat="General Surgery", us="$8,000–$15,000", th="$2,500–$5,000",
        stay="4–7 nights",
        hosps=["Bangkok Hospital Chiang Mai", "Chiang Mai Ram Hospital", "Bumrungrad International Hospital"],
        blurb=("Inguinal/umbilical/incisional repair, open or laparoscopic, mesh brands identical to US ORs. A tidy fly-in procedure with fast recovery."),
        notes="No heavy lifting for weeks after — the beach part of the recovery plan writes itself."),
    "Liver Transplant": dict(
        cat="General Surgery", us="$500,000–$800,000", th="Not available to foreign patients",
        stay="—",
        hosps=[],
        blurb=(
            "Another honesty box: **deceased-donor organ transplantation in Thailand is restricted "
            "to Thai nationals** — the Red Cross allocation system does not list foreigners, and "
            "reputable hospitals follow it. Transplant-tourism brokers promising Thai livers are "
            "lying to desperate people; we refuse to."),
        notes="Living-donor programs for foreigners exist in other countries with real legal frameworks (e.g., India with a related donor, Turkey, South Korea). Intake call before you spend a dollar anywhere — the scam density in transplant tourism is the worst in the industry."),

    # ---- General Surgery (honesty box)
    "Kidney Transplant": dict(
        cat="General Surgery", us="$260,000–$450,000", th="Not available to foreign patients",
        stay="—", hosps=[],
        blurb=(
            "Honesty box: **kidney transplantation in Thailand is effectively closed to "
            "foreigners.** Deceased-donor organs are allocated to Thai nationals through the Red "
            "Cross system, and living-donor programs require documented close kinship reviewed "
            "by committee — a bar a visiting patient cannot clear. Anyone selling you a Thai "
            "kidney is selling you organ trafficking, full stop."),
        notes="Where the honest map points instead: living-related-donor programs in India, Turkey or Mexico under real legal frameworks, or staying on your US list with Thai-priced dialysis care in between — yes, that's a real strategy, ask us."),

    # ---- Diagnostics & Check-Ups
    "Executive Health Check-Ups": dict(
        cat="Diagnostics & Check-Ups", us="$2,000–$5,000", th="$400–$1,200",
        stay="1–2 days; results debrief before you fly",
        hosps=["Bumrungrad International Hospital", "Bangkok Hospital", "MedPark Hospital", "Bangkok Hospital Chiang Mai", "Lanna Hospital"],
        blurb=(
            "The famous Thai hospital checkup: a tiered menu (labs, imaging, cardiac stress, "
            "scopes at the upper tiers), all results same-week with a physician sit-down. It's "
            "the lowest-friction first date with Thai healthcare — fly in skeptical, fly out "
            "with a binder of data and change for the money a US colonoscopy costs."),
        notes="Pick the tier by age and risk factors, not by what's shiniest — we map your history to the right panel and cut the upsells."),
    "Full Body MRI": dict(
        cat="Diagnostics & Check-Ups", us="$2,500–$5,000", th="$700–$1,500",
        stay="Same-day scan; results in 1–3 days",
        hosps=["Bumrungrad International Hospital", "Bangkok Hospital", "MedPark Hospital"],
        blurb=(
            "The Prenuvo-style whole-body screening MRI, at a Thai hospital price instead of a "
            "venture-funded one. Genuinely good at finding things early; also genuinely good at "
            "finding harmless things that will haunt your anxiety."),
        notes="The incidentaloma problem is real: before you scan, decide with us who will follow up any finding, where, and for how much. Screening without a follow-up path is expensive anxiety."),
    "CT Scan": dict(
        cat="Diagnostics & Check-Ups", us="$1,000–$3,000", th="$200–$600",
        stay="Same-day",
        hosps=["Bumrungrad International Hospital", "Bangkok Hospital Chiang Mai", "Lanna Hospital"],
        blurb=(
            "Coronary calcium scores, low-dose lung screening, and diagnostic CT on modern "
            "scanners, often bookable within days. The calcium score in particular is the "
            "cheapest genuinely useful cardiac data most Americans have never been offered."),
        notes="CT is ionizing radiation — scan with a reason (age, smoking history, symptoms, surveillance), not for the collector's album."),
    "Genetic Testing": dict(
        cat="Diagnostics & Check-Ups", us="$250–$5,000", th="$300–$1,500",
        stay="Blood draw; results in 2–4 weeks (remote debrief fine)",
        hosps=["Bumrungrad International Hospital", "MedPark Hospital", "Samitivej Sukhumvit Hospital"],
        blurb=(
            "Hereditary cancer panels (BRCA and friends), cardiac risk panels, carrier "
            "screening, and pharmacogenomics — which drugs your liver actually metabolizes — "
            "at Thai lab prices with physician counseling attached."),
        notes="Actionable beats interesting: we steer toward panels with medical consequences and real genetic counseling, not ancestry-adjacent entertainment."),

    # ---- Futuristic Thai Therapies (NaN's 3-paragraph spec: experience / cost / science)
    "Stem Cell Therapy": dict(
        cat="Futuristic Thai Therapies", us="Largely unavailable / trial-only", th="$5,000–$20,000 program range",
        stay="Program-dependent, typically 1–2 weeks",
        hosps=["MedPark Hospital", "Bumrungrad International Hospital"],
        blurb=(
            "The flagship of the 'therapies the FDA sits on' category — handled with adult "
            "supervision. Thailand permits certain regenerative treatments (orthopedic PRP/BMAC, "
            "some mesenchymal stem-cell protocols) under Ministry of Public Health regulation, "
            "alongside a gray market of miracle-cure clinics we will not send you to."),
        science=(
            "Graded: **promising-to-mixed for orthopedic indications** (knee osteoarthritis has "
            "real trials with modest effects), **experimental for autoimmune conditions**, and "
            "**unproven for anti-aging and most of what Instagram sells**. Cell source, handling "
            "and dose vary wildly between clinics — that variance, not the concept, is the risk."),
        notes="Our rule: regulated facility, named physician, published protocol, no cure-words. A clinic that promises to cure ALS, autism or aging gets blacklisted — by us and by you."),
    "Hyperbaric Oxygen Therapy (HBOT)": dict(
        cat="Futuristic Thai Therapies", us="$250–$600 per session", th="$80–$250 per session",
        stay="Course-based; pairs with any Chiang Mai stay",
        hosps=["Bangkok Hospital", "Bumrungrad International Hospital"],
        blurb=(
            "An hour or two at pressure breathing pure oxygen — hospital hard chambers here, "
            "plus a growing wellness-clinic scene. Divers know it as the bends fix; the longevity "
            "crowd knows it as the current darling."),
        science=(
            "Graded: **proven for its approved indications** — decompression sickness, chronic "
            "wounds, radiation tissue injury, certain infections. **Unproven but actively "
            "researched** for cognition and 'rejuvenation' (small Israeli trials, big headlines). "
            "A soft-shell spa chamber at 1.3 ATA is not the same instrument as a hospital "
            "chamber at 2.4 ATA — know which one you're buying."),
        notes="Medical indication → hospital chamber, always. Wellness protocol → we'll book the reputable one and tell you plainly which claims outrun the data."),
    "Whole-Body Cryotherapy": dict(
        cat="Futuristic Thai Therapies", us="$40–$90 per session", th="$30–$70 per session",
        stay="Minutes; add-on to anything",
        hosps=[],
        blurb=("Three minutes at −110°C in your underwear and gloves. Athletes swear by it, "
               "Instagram loves it, and in Thailand it costs less than the smoothie after."),
        science=("Graded: **plausible for short-term recovery and mood, thin for everything "
                 "else.** Trials show reduced soreness perception; hard performance and "
                 "longevity outcomes haven't materialized. Low risk at legitimate operators."),
        notes="Fun, cheap, probably mildly useful, definitely not medicine. We file it under recovery-holiday garnish."),
    "NAD+ IV Therapy": dict(
        cat="Futuristic Thai Therapies", us="$500–$1,000 per infusion", th="$150–$400 per infusion",
        stay="2–4 hours per infusion",
        hosps=[],
        blurb=("The longevity scene's favorite drip, at Thai wellness-clinic prices. Slow "
               "infusion, flushing is normal, evangelists are plentiful."),
        science=("Graded: **true premise, unproven product.** Cellular NAD+ does decline with "
                 "age; that IV repletion improves human aging outcomes is exactly the part "
                 "without convincing trials. Oral precursors (NR/NMN) have better-studied "
                 "pharmacology at a fraction of the cost."),
        notes="If you want it, licensed physician clinic only, and we'll price the oral-precursor comparison next to it — defiance includes defying the wellness industry's markup."),
    "Placenta Extract Infusions": dict(
        cat="Futuristic Thai Therapies", us="Not available (unapproved)", th="$100–$300 per session",
        stay="Clinic visit; often sold as courses",
        hosps=[],
        blurb=("Laennec-style human-placenta hydrolysate injections — a Japanese longevity-"
               "clinic staple that migrated to Thai anti-aging medicine. Popular for skin, "
               "fatigue and menopause claims."),
        science=("Graded: **weak.** Decades of use in Japan, a handful of small trials (some "
                 "menopause-symptom signals), no robust evidence for rejuvenation. The entire "
                 "question is sourcing and licensing — pharmaceutical-grade product at a "
                 "physician clinic or nothing."),
        notes="We only book licensed clinics using registered pharmaceutical product, and we say the evidence grade out loud before you pay."),
    "Exosome Therapy": dict(
        cat="Futuristic Thai Therapies", us="Trial-only", th="$2,000–$8,000 per program",
        stay="Program-dependent",
        hosps=[],
        blurb=("Cell-free vesicles harvested from stem-cell cultures, sold as the next "
               "generation of regenerative medicine — for skin, joints, hair, and increasingly "
               "for everything, which is the tell."),
        science=("Graded: **exciting biology, zero approved indications anywhere.** Early human "
                 "data is sparse and heterogeneous; product characterization varies clinic to "
                 "clinic. Regulatory status is gray even in permissive jurisdictions."),
        notes="We treat exosomes like we treat any frontier: slowly, at regulated facilities, with your eyes open and our grade in writing."),
    "Peptide Injections": dict(
        cat="Futuristic Thai Therapies", us="Gray-market / compounding-pharmacy limbo", th="$100–$500 per cycle",
        stay="Self-administered courses after physician start",
        hosps=[],
        blurb=("BPC-157, TB-500, GHK-Cu and the rest of the recovery-peptide alphabet — "
               "physician-supervised at Thai longevity clinics rather than mystery vials from "
               "the internet."),
        science=("Graded: **animal-data-rich, human-trial-poor.** Mechanisms are plausible, "
                 "anecdotes are loud, controlled human evidence is nearly absent. The dominant "
                 "real-world risk is product purity — which is precisely what physician "
                 "sourcing addresses."),
        notes="Supervised or nothing. If your protocol came from a podcast, bring it to the intake call and we'll pressure-test it together."),
    "Vagus Nerve Stimulation": dict(
        cat="Futuristic Thai Therapies", us="$30,000–$50,000 (implanted)", th="$12,000–$25,000 (implanted); wearables $200–$500",
        stay="Implant: 5–10 nights; wearables: none",
        hosps=["Bangkok Hospital", "Bumrungrad International Hospital"],
        blurb=("Two different products wearing one name: implanted VNS — real neurosurgery for "
               "drug-resistant epilepsy and depression — and ear-clip taVNS wearables sold for "
               "stress and sleep."),
        science=("Graded: **implanted VNS is established medicine** with decades of evidence for "
                 "its indications. **taVNS wearables are promising-but-unsettled** — real "
                 "physiology, mixed small trials, low risk."),
        notes="Implant candidates get the full neurology workup pathway; gadget-curious clients get told it's a $300 experiment, not a treatment plan."),
    "Bioresonance Therapy": dict(
        cat="Futuristic Thai Therapies", us="$100–$300 per session", th="$30–$80 per session",
        stay="Clinic visit",
        hosps=[],
        blurb=("Electrodes, a box with dials, and the claim that your cells' 'frequencies' can "
               "be read and retuned. Widely available in Thai wellness centers."),
        science=("Graded: **no plausible mechanism, no credible trials.** We are a defiant "
                 "company, not a dishonest one: this one is vibes. If the ritual relaxes you, "
                 "that's worth something — just not a diagnosis."),
        notes="We'll book it if you want the experience; we will never let a bioresonance readout change your actual medical plan."),
    "EBOO Blood Ozone Dialysis": dict(
        cat="Futuristic Thai Therapies", us="$1,000–$2,500 per session (fringe clinics)", th="$300–$800 per session",
        stay="2–3 hours per session",
        hosps=[],
        blurb=("Extracorporeal blood oxygenation and ozonation — your blood run through a "
               "filter, mixed with ozone, and returned. The maximalist end of the ozone "
               "wellness spectrum, heavily marketed to biohackers."),
        science=("Graded: **unproven and not risk-free.** Ozone is a potent oxidizer; controlled "
                 "human outcome data for EBOO is essentially absent. Anything that pumps your "
                 "blood outside your body lives or dies on the operator's sterile technique."),
        notes="If you insist: licensed physician facility with real extracorporeal-circuit experience, or we walk. Our grade goes in writing either way."),
    "Ozone Autohemotherapy": dict(
        cat="Futuristic Thai Therapies", us="$150–$400 per session", th="$60–$150 per session",
        stay="Under an hour",
        hosps=[],
        blurb=("The smaller sibling: a syringe of your blood mixed with ozone and reinfused. "
               "A fixture of integrative clinics from Bangkok to Berlin."),
        science=("Graded: **decades of use, still no convincing controlled evidence** for the "
                 "immune and energy claims. Lower mechanical risk than EBOO by dose and "
                 "simplicity."),
        notes="Same rule as all ozone: licensed clinic, sterile circuit, honest grade — and it never substitutes for treating an actual diagnosis."),
    "Therapeutic Plasma Exchange": dict(
        cat="Futuristic Thai Therapies", us="$5,000–$10,000 per session", th="$2,000–$4,000 per session",
        stay="Half-day per session; courses vary",
        hosps=["Bumrungrad International Hospital", "Bangkok Hospital", "MedPark Hospital"],
        blurb=("Apheresis: plasma out, replacement in. A real hospital procedure for "
               "neurological and autoimmune disease — recently rebranded by the longevity world "
               "as 'plasma dilution' anti-aging."),
        science=("Graded: **established medicine for its real indications; speculative for "
                 "longevity.** The aging interest traces to legitimate dilution research in "
                 "mice and small human pilots — intriguing, unproven, expensive."),
        notes="We book TPE at hospital apheresis units only — this is not a strip-mall procedure. Longevity buyers get the mouse-study caveat verbatim."),
    "Chelation Therapy IV": dict(
        cat="Futuristic Thai Therapies", us="$100–$300 per session (long courses)", th="$100–$250 per session",
        stay="Hours per session; courses run weeks",
        hosps=[],
        blurb=("EDTA drips: genuine toxicology for confirmed heavy-metal poisoning, and a "
               "long-running alternative-medicine offering for 'detox' and heart disease."),
        science=("Graded: **proven for documented heavy-metal toxicity — full stop.** For "
                 "cardiovascular disease the giant TACT trial showed at best a modest signal in "
                 "diabetics that follow-ups haven't cleanly settled; for 'general detox' there "
                 "is nothing to detox. Real electrolyte and kidney risks without monitoring."),
        notes="Confirmed exposure and labs first — we'll arrange the actual toxicology. Chelation as a lifestyle is a hard no from us."),
    "NK Cell Therapy": dict(
        cat="Futuristic Thai Therapies", us="Trial-only", th="$8,000–$20,000 per program",
        stay="1–2 weeks per cycle",
        hosps=[],
        blurb=("Your natural-killer cells drawn, expanded in a lab for weeks, and reinfused — "
               "sold across Asia's longevity clinics as immune optimization, and studied "
               "seriously in oncology elsewhere."),
        science=("Graded: **real immunology, real oncology trials, no proven commercial "
                 "product.** Expansion quality varies enormously between labs; 'immune boosting' "
                 "for healthy people has no outcome evidence at all."),
        notes="Cancer patients: this conversation belongs with your oncologist and a tumor board, and we'll help you have it there. Wellness buyers: we grade it experimental and price the opportunity cost."),
    "Glutathione Whitening IVs": dict(
        cat="Futuristic Thai Therapies", us="$150–$400 per session", th="$30–$80 per session",
        stay="Under an hour; sold in courses",
        hosps=[],
        blurb=("The master-antioxidant drip, ubiquitous in Thai beauty clinics — marketed for "
               "skin brightening and general glow, priced like a coffee habit rather than a "
               "procedure."),
        science=("Graded: **weak for whitening, fine-ish for safety at licensed clinics.** "
                 "Skin-lightening evidence is small and short-term; no regulator anywhere has "
                 "approved IV glutathione for it. Adverse events cluster at unlicensed "
                 "operators."),
        notes="No judgment on the goal — it's a huge, normal part of the beauty landscape here. Licensed clinic, honest expectations, and we'll tell you what topical dermatology does better."),
    "IV Laser Therapy": dict(
        cat="Futuristic Thai Therapies", us="Rare / fringe", th="$50–$150 per session",
        stay="Under an hour",
        hosps=[],
        blurb=("Intravenous laser blood irradiation — a fiber-optic thread lighting up your "
               "bloodstream, descended from Soviet-era laser medicine and alive in Asian "
               "integrative clinics."),
        science=("Graded: **mechanistically speculative, clinically unproven.** Photobiomodulation "
                 "is a real research field; running it intravenously has never produced sound "
                 "human outcome trials."),
        notes="Low-harm at licensed clinics, low-evidence everywhere. We file it with bioresonance: bookable, graded honestly, never a substitute for medicine."),
    "Shockwave Therapy": dict(
        cat="Futuristic Thai Therapies", us="$300–$500 per session", th="$50–$150 per session",
        stay="Sessions over weeks; pairs with a long stay",
        hosps=["Bangkok Hospital Chiang Mai", "Chiang Mai Ram Hospital"],
        blurb=("Extracorporeal shockwave for stubborn tendons — plantar fasciitis, tennis "
               "elbow, calcific shoulder — at sports-medicine departments and physio clinics "
               "across Thailand."),
        science=("Graded: **actually decent.** Among the best-evidenced items in this entire "
                 "index for chronic tendinopathies; effects accumulate over a course. The ED "
                 "and cellulite marketing runs far ahead of that evidence."),
        notes="One of the quiet wins of this list: cheap here, evidence-backed for the right diagnosis, and it makes a recovery month in Chiang Mai productive."),
}

# ---------------------------------------------------------------- hospitals
HOSPITALS = {
    "Bumrungrad International Hospital": dict(
        city="Bangkok", type="Private international hospital", jci=True, beds="580",
        blurb=(
            "The name Americans know. One of the first hospitals outside the US to be JCI-"
            "accredited (2002) and still the reference point for international patient care in "
            "Asia — 30+ specialty centers, interpreters for dozens of languages, and an "
            "international-patient wing that processes more foreign patients than some countries' "
            "entire systems."),
        strengths=["Executive health screening", "Cardiology", "Orthopedics", "Oncology (Horizon Center)", "Complex multi-specialty cases"]),
    "Bangkok Hospital": dict(
        city="Bangkok", type="Private flagship (BDMS network)", jci=True, beds="550+",
        blurb=(
            "Flagship of BDMS, Thailand's largest private hospital group. The campus includes the "
            "Bangkok Heart Hospital and Wattanosoth Cancer Hospital — dedicated cardiac and "
            "oncology facilities rather than departments. If your case is complex and multi-"
            "disciplinary, this is one of the two default answers in Bangkok."),
        strengths=["Cardiac surgery & intervention", "Oncology (Wattanosoth)", "Neurosurgery & spine", "Trauma & orthopedics"]),
    "Samitivej Sukhumvit Hospital": dict(
        city="Bangkok", type="Private international hospital (BDMS)", jci=True, beds="270+",
        blurb=(
            "The expat-neighborhood hospital of Bangkok — strong women's health, pediatrics, and "
            "surgical departments with a service culture calibrated for foreign residents. Often "
            "the comfortable choice for mid-complexity surgical work."),
        strengths=["Women's health", "Plastic & reconstructive surgery", "GI & general surgery", "Pediatrics"]),
    "BNH Hospital": dict(
        city="Bangkok", type="Private hospital (est. 1898)", jci=True, beds="120",
        blurb=(
            "Bangkok's oldest private hospital, founded 1898 to treat foreign residents — medical "
            "tourism before the phrase existed. Boutique-scale, strong in spine, women's health "
            "and fertility, with the unhurried feel big flagships can't fake."),
        strengths=["Spine center", "Fertility & IVF", "Women's health", "Orthopedics"]),
    "MedPark Hospital": dict(
        city="Bangkok", type="Private tertiary hospital (opened 2020)", jci=True, beds="550 capacity",
        blurb=(
            "The new heavyweight — purpose-built in 2020 around complex tertiary care, staffed "
            "heavily with university-hospital professors, and priced aggressively to win exactly "
            "the complicated cases other private hospitals refer out. Serious medicine, new "
            "building, ambitions to match."),
        strengths=["Complex oncology", "Cardiac & structural heart", "Nephrology & transplant medicine", "Critical care"]),
    "Vejthani Hospital": dict(
        city="Bangkok", type="Private international hospital", jci=True, beds="500 capacity",
        blurb=(
            "Quietly one of the highest-volume medical-tourism hospitals in Bangkok, with "
            "particular depth in orthopedics (joint replacement packages are a house specialty) "
            "and a large Middle Eastern and Central Asian patient base — which tells you their "
            "international logistics are battle-tested."),
        strengths=["Joint replacement packages", "Spine surgery", "Dental center", "General surgery"]),
    "Praram 9 Hospital": dict(
        city="Bangkok", type="Private hospital", jci=True, beds="313",
        blurb=(
            "Mid-size private hospital known for cardiology and kidney care at prices a notch "
            "below the famous names — a value pick for cardiac intervention with JCI paperwork "
            "intact."),
        strengths=["Cardiology & cath lab", "Nephrology & dialysis", "Health screening"]),
    "Phyathai 2 Hospital": dict(
        city="Bangkok", type="Private hospital (Phyathai group)", jci=True, beds="260+",
        blurb=(
            "Solid all-rounder in the Phyathai/Paolo network with an established international "
            "patient center — frequently the sharper-priced quote on mid-complexity surgical "
            "work in Bangkok."),
        strengths=["Orthopedics", "Cardiology", "General surgery", "Health checkups"]),
    "Yanhee International Hospital": dict(
        city="Bangkok", type="Private hospital — cosmetic & GA surgery at scale", jci=True, beds="400",
        blurb=(
            "A full general hospital that happens to run one of the largest cosmetic-surgery "
            "operations on the planet — dozens of plastic surgeons, published package prices, "
            "and four decades of gender-affirming surgical experience. High-volume, "
            "process-driven, unpretentious about it."),
        strengths=["Cosmetic surgery at volume", "Gender affirmation surgery", "Bariatric surgery", "Hair transplant"]),
    "Kamol Cosmetic Hospital": dict(
        city="Bangkok", type="Specialist cosmetic & gender-affirmation hospital", jci=False, beds="Specialist facility",
        blurb=(
            "Founded by Dr. Kamol Pansritum, one of the most experienced gender-affirming "
            "surgeons worldwide (tens of thousands of GA procedures across a career). A purpose-"
            "built GA and cosmetic hospital: FFS, vaginoplasty, top surgery, body work — this is "
            "a destination facility for exactly the care US legislatures are busy criminalizing."),
        strengths=["Vaginoplasty & GA surgery", "Facial feminization (FFS)", "Top surgery", "Body contouring"]),
    "Preecha Aesthetic Institute": dict(
        city="Bangkok", type="Specialist plastic-surgery institute", jci=False, beds="Clinic + partner hospitals",
        blurb=(
            "The lineage institution — Dr. Preecha Tiewtranon trained a large share of Thailand's "
            "GA surgeons and the institute carries five decades of technique history. Boutique "
            "scale, operating with partner hospitals for major cases."),
        strengths=["Gender affirmation surgery", "Facial plastic surgery", "Revision & complex aesthetic cases"]),
    "Suporn Clinic": dict(
        city="Chonburi", type="Specialist GA surgery clinic", jci=False, beds="Dedicated clinic + hospital partner",
        blurb=(
            "Internationally famous vaginoplasty practice (Dr. Suporn's technique is cited in the "
            "surgical literature; practice continued by Dr. Bank). Long waitlists, strict "
            "requirements, devoted alumni community — the definition of destination surgery."),
        strengths=["Vaginoplasty (signature technique)", "Structured long-stay recovery program"]),
    "Jetanin Institute": dict(
        city="Bangkok", type="Specialist fertility hospital", jci=True, beds="Specialist facility",
        blurb=(
            "Thailand's best-known dedicated IVF hospital — full in-house embryology, PGT lab, "
            "and decades of protocol depth. Operates strictly within the Thai ART Act, which is "
            "what you want from an embryo lab."),
        strengths=["IVF & ICSI", "PGT-A genetic testing", "Egg freezing"]),
    "Superior A.R.T.": dict(
        city="Bangkok", type="Specialist IVF & genetics center", jci=False, beds="Specialist facility",
        blurb=(
            "Australian-partnered assisted-reproduction center (Sydney IVF lineage) with a strong "
            "genetics lab — the technical-credentials pick for PGT-heavy cases."),
        strengths=["IVF with advanced genetics (PGT)", "Egg freezing", "Recurrent-loss workups"]),
    "Rutnin Eye Hospital": dict(
        city="Bangkok", type="Specialist eye hospital (est. 1964)", jci=True, beds="Specialist facility",
        blurb=(
            "Thailand's oldest dedicated eye hospital — everything from LASIK to vitreoretinal "
            "surgery under one roof, with subspecialists you'd otherwise chase across three US "
            "referrals."),
        strengths=["LASIK/refractive", "Cataract & premium IOL", "Retina & vitreous", "Cornea"]),
    "Bangkok International Dental Center": dict(
        city="Bangkok", type="Specialist dental center", jci=False, beds="70+ treatment rooms",
        blurb=(
            "One of the largest dedicated dental-tourism facilities in Asia — implantology, "
            "full-mouth rehabilitation and cosmetic dentistry with in-house labs and same-week "
            "turnarounds built for fly-in patients."),
        strengths=["Implants & All-on-X", "Veneers & smile makeovers", "Full-mouth rehabilitation"]),
    "Bangkok Hospital Chiang Mai": dict(
        city="Chiang Mai", type="Private hospital (BDMS network)", jci=True, beds="140+",
        blurb=(
            "The shiny BDMS outpost in our home city — modern plant, international patient desk, "
            "and the strongest specialist bench in the north for cardiac and orthopedic work. "
            "Where we point visitors who want Bangkok-grade facilities without Bangkok."),
        strengths=["Orthopedics", "Cardiology & cath lab", "Health screening", "International patient services"]),
    "Chiang Mai Ram Hospital": dict(
        city="Chiang Mai", type="Private hospital", jci=False, beds="350+",
        blurb=(
            "The workhorse private hospital of Chiang Mai and the one long-term expats actually "
            "use — big specialist roster, 24/7 everything, prices a clear step below Bangkok. "
            "Thai hospital accreditation (HA) rather than JCI; ask us what that difference does "
            "and doesn't mean."),
        strengths=["General & laparoscopic surgery", "Orthopedics & sports medicine", "Cosmetic procedures", "Emergency care"]),
    "McCormick Hospital": dict(
        city="Chiang Mai", type="Private mission hospital (est. 1888)", jci=False, beds="400",
        blurb=(
            "Chiang Mai's grand old mission hospital — over 130 years serving the city, honest "
            "pricing, and deep community trust. Not a medical-tourism showroom; exactly why "
            "locals and long-stayers rate it."),
        strengths=["General medicine & surgery", "Maternity", "Straightforward pricing"]),
    "Sriphat Medical Center": dict(
        city="Chiang Mai", type="Private wing of Chiang Mai University Faculty of Medicine", jci=False, beds="University-affiliated",
        blurb=(
            "The private-service arm of CMU's medical school (alongside Maharaj Nakorn / Suan Dok "
            "hospital) — professor-level specialists at private-clinic convenience. For complex "
            "diagnostics in the north, this is where the deep bench lives. Also: it's แถวหลังมอ — "
            "right in our neighborhood."),
        strengths=["University-professor specialists", "Complex diagnostics", "Oncology & hematology", "Orthopedics"]),
    "Lanna Hospital": dict(
        city="Chiang Mai", type="Private hospital", jci=False, beds="180",
        blurb=(
            "Established mid-size private hospital on the Superhighway — competent, quick, and "
            "often the sharpest quote in town for imaging, checkups and routine surgery."),
        strengths=["Health checkups & imaging", "General surgery", "Value pricing"]),
    "Bangkok Hospital Phuket": dict(
        city="Phuket", type="Private hospital (BDMS network)", jci=True, beds="230+",
        blurb=(
            "The serious hospital of the beach south — full surgical services with an "
            "international patient machine tuned by decades of tourist trauma and planned "
            "procedures alike. Anchor for recover-by-the-sea itineraries."),
        strengths=["Cosmetic surgery packages", "Orthopedics", "International patient services", "Recovery-holiday logistics"]),
}

# ---------------------------------------------------------------- destinations
DESTINATIONS = {
    "Thailand": dict(
        blurb=(
            "The country that made medical tourism a real industry. World-class private hospitals "
            "(more JCI-accredited facilities than nearly anywhere else in Asia), English-speaking "
            "specialists trained in the US/UK/Australia/Japan, and prices 50–80% below US rates — "
            "not because the medicine is worse, but because the billing isn't a weapon."),
        legal=[
            "**Medical treatment visa (Non-Immigrant O / MT):** 60-day visa-exempt entry covers most procedures; longer treatment supports a medical visa or extension — part of what we arrange.",
            "**Surrogacy: banned for foreigners** (2015 ART Act). Anyone selling it is selling a crime.",
            "**IVF:** legally married heterosexual couples only; certificate required; no sex selection.",
            "**Organ transplants:** deceased-donor allocation is restricted to Thai nationals — no foreigner waitlist exists.",
            "**Cannabis:** decriminalized status keeps shifting under new regulation — current rules at intake, not from a 2022 headline.",
            "**Pharmacies:** many US-prescription drugs are OTC or cheaply prescribed here (HRT, PrEP, most chronic-disease meds) — bring your records.",
        ],
        practical=(
            "Direct-ish routing from most US hubs via Tokyo/Seoul/Taipei/Doha; strong 4G/5G "
            "everywhere; ubiquitous cashless payment; hospital interpreters standard at "
            "international desks. Power sockets take US plugs. Your phone works, your apps work, "
            "your body costs 80% less to repair.")),
    "Chiang Mai": dict(
        blurb=(
            "Our home base. Northern Thailand's university city — calm, walkable neighborhoods, "
            "a real medical ecosystem (a medical school, four sizable private hospitals, dental "
            "and dermatology everywhere), and a cost of living that makes long recovery stays "
            "trivial: comfortable serviced apartments run $400–800/month, not $400/night. "
            "This is where NaN fixed her military dental work fifteen years ago and never "
            "really left."),
        legal=[
            "Best for: dental, orthopedic, cosmetic, screening, and any care with a long recovery tail where housing costs dominate.",
            "For rare-subspecialty surgery, Bangkok's flagship depth sometimes wins — we say so when it does, then fly you back here to recover where it's cheap and quiet.",
            "**Burning season (roughly Feb–Apr):** air quality gets genuinely bad. If you have respiratory anything, we schedule around it — honesty over occupancy.",
        ],
        practical=(
            "Hospitals we work with here: [[Bangkok Hospital Chiang Mai]], [[Chiang Mai Ram Hospital]], "
            "[[McCormick Hospital]], [[Sriphat Medical Center]], [[Lanna Hospital]]. Find us แถวหลังมอ — "
            "behind the university, where the good coffee is.")),
    "Bangkok": dict(
        blurb=(
            "The heavyweight division. The largest concentration of JCI-accredited hospitals in "
            "Southeast Asia, subspecialists in everything, and the world's deepest bench for "
            "gender-affirming surgery. If your case is complex, rare, or multi-specialty, "
            "Bangkok is usually the answer — and it's a 70-minute flight from our door."),
        legal=[
            "Best for: cardiac, oncology, complex spine, fertility, GA surgery, anything requiring a tumor board or a subspecialist per organ.",
            "Recovery in Bangkok is doable but urban; many clients do surgery in Bangkok, recovery in Chiang Mai or Phuket. We run that relay constantly.",
        ],
        practical=(
            "Anchors: [[Bumrungrad International Hospital]], [[Bangkok Hospital]], [[MedPark Hospital]], "
            "[[Samitivej Sukhumvit Hospital]], [[Vejthani Hospital]], [[BNH Hospital]], plus the "
            "specialist houses — [[Kamol Cosmetic Hospital]], [[Yanhee International Hospital]], "
            "[[Rutnin Eye Hospital]], [[Jetanin Institute]], [[Bangkok International Dental Center]].")),
    "Phuket": dict(
        blurb=(
            "Surgery with a sea view — more precisely, surgery at a serious BDMS hospital "
            "followed by recovery somewhere your biggest obligation is choosing lunch. Strongest "
            "for cosmetic packages, orthopedics, dental, and checkups wrapped in an actual "
            "vacation."),
        legal=[
            "Best for: cosmetic surgery packages, joint work with beach rehab, dental trips, family-accompanied recoveries.",
            "Not the play for complex tertiary care — that's Bangkok, one hour away.",
        ],
        practical=(
            "Anchor: [[Bangkok Hospital Phuket]]. Direct international flights mean some clients "
            "never touch Bangkok at all.")),
}
