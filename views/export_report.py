"""
Export Report — complete career PDF including predicted roles and comparison.
"""

import streamlit as st
import io
from datetime import datetime
from engine.data_loader import load_roles, get_skills_for_role
from engine.skill_matcher import compute_compatibility
from engine.simulator import recommend_top_improvements
from utils.helpers import score_to_band, format_salary, format_growth
from config import MIN_IMPORTANCE_THRESHOLD


def generate_pdf(role_title, score, band, role, result, top_recs, phases, total_weeks, ai_predictions=None, ct_result=None):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer,
            Table, TableStyle, HRFlowable, PageBreak,
        )
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
            rightMargin=2*cm, leftMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm)
        S = getSampleStyleSheet()

        def ps(name, parent="Normal", **kw):
            return ParagraphStyle(name, parent=S[parent], **kw)

        T  = ps("T",  "Title",    fontSize=22, spaceAfter=4,  textColor=colors.HexColor("#7F77DD"))
        SB = ps("SB", "Normal",   fontSize=11, spaceAfter=16, textColor=colors.grey)
        H2 = ps("H2", "Heading2", fontSize=13, spaceBefore=14, spaceAfter=6,  textColor=colors.HexColor("#1D9E75"))
        H3 = ps("H3", "Heading3", fontSize=11, spaceBefore=10, spaceAfter=4,  textColor=colors.HexColor("#7F77DD"))
        BD = ps("BD", "Normal",   fontSize=10, leading=14,    spaceAfter=4, wordWrap='CJK')
        SM = ps("SM", "Normal",   fontSize=9,  textColor=colors.grey, spaceAfter=4)

        story = []

        # ── Cover ──────────────────────────────────────────────────────────
        story += [
            Paragraph("CareerSight", T),
            Paragraph("An Explainable AI-Based Career Guidance and Skill Gap Analysis System", SB),
            HRFlowable(width="100%", thickness=1, color=colors.HexColor("#7F77DD33")),
            Spacer(1, 8),
            Paragraph(f"Report generated: {datetime.now().strftime('%d %B %Y, %H:%M')}", SM),
            Paragraph(f"Target Role: <b>{role_title}</b>", BD),
            Spacer(1, 8),
        ]

        # ── Part 1: Compatibility Summary ──────────────────────────────────
        story.append(Paragraph("Part 1 — Target Role Analysis", H2))
        story += [
            Paragraph(f"<b>Target Role:</b> {role_title}", BD),
            Paragraph(f"<b>Category:</b> {role.get('category','–')}", BD),
            Paragraph(f"<b>Compatibility Score:</b> {score:.1f}% — {band}", BD),
        ]
        sal = role.get("salary_range", {})
        tbl = Table([
            ["Salary Range", format_salary(sal)],
            ["Demand Level", role.get("demand_level","–")],
            ["Growth Rate",  format_growth(role.get("growth_rate",0))],

        ], colWidths=[4*cm, 12*cm])
        tbl.setStyle(TableStyle([
            ("FONTSIZE",(0,0),(-1,-1),9),
            ("TEXTCOLOR",(0,0),(0,-1),colors.grey),
            ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
            ("BOTTOMPADDING",(0,0),(-1,-1),4),
            ("TOPPADDING",(0,0),(-1,-1),4),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
        ]))
        story += [tbl, Spacer(1, 6)]
        if role.get("description"):
            story.append(Paragraph("<b>Description:</b>", BD))
            # Use a table cell for description so it wraps within page margins
            desc_tbl = Table(
                [[Paragraph(role["description"], BD)]],
                colWidths=[16*cm]
            )
            desc_tbl.setStyle(TableStyle([
                ("LEFTPADDING",(0,0),(-1,-1), 0),
                ("RIGHTPADDING",(0,0),(-1,-1), 0),
                ("TOPPADDING",(0,0),(-1,-1), 0),
                ("BOTTOMPADDING",(0,0),(-1,-1), 4),
            ]))
            story.append(desc_tbl)
        story.append(Spacer(1, 10))

        # ── Skill Profile ──────────────────────────────────────────────────
        story.append(Paragraph("Skill Profile", H3))
        rows = [["Skill", "Your Level", "Required", "Gap", "Status"]]
        for s in sorted(result["strengths"] + result["gaps"],
                        key=lambda x: x["importance"], reverse=True)[:15]:
            rows.append([
                s["skill_name"],
                f"{s['user_level']:.2f}",
                f"{s['importance']:.2f}",
                f"{max(0, s['importance']-s['user_level']):.2f}",
                "Met" if s["user_level"] >= s["importance"] else "Gap",
            ])
        st2 = Table(rows, colWidths=[6*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
        st2.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#7F77DD33")),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),9),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, colors.HexColor("#F8F8FF")]),
            ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#DDDDDD")),
            ("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("TOPPADDING",(0,0),(-1,-1),5),
        ]))
        story += [st2, Spacer(1, 10)]

        # ── Top Recommendations ────────────────────────────────────────────
        if top_recs:
            story.append(Paragraph("Top Skills to Learn Next", H3))
            story.append(Paragraph(
                "Skills providing highest score improvement if developed by one level (+0.3):", BD))
            rec_rows = [["#", "Skill", "Category", "Score Gain", "Level Needed"]]
            for i, r in enumerate(top_recs, 1):
                rec_rows.append([str(i), r["skill_name"], r["category"],
                                  f"+{r['score_gain']:.1f}%", r["level_required"]])
            rt = Table(rec_rows, colWidths=[1*cm, 6*cm, 4*cm, 3*cm, 3*cm])
            rt.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#7F77DD33")),
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                ("FONTSIZE",(0,0),(-1,-1),9),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, colors.HexColor("#F5F5FF")]),
                ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#DDDDDD")),
                ("BOTTOMPADDING",(0,0),(-1,-1),5),
                ("TOPPADDING",(0,0),(-1,-1),5),
            ]))
            story += [rt, Spacer(1, 10)]

        # ── Full Learning Path ─────────────────────────────────────────────
        if phases:
            story.append(Paragraph("Full Learning Path", H2))
            story.append(Paragraph(
                f"Estimated total: {total_weeks} weeks at 8–10 hours per week.", BD))
            story.append(Spacer(1, 6))
            for phase in phases:
                story.append(Paragraph(f"<b>{phase['name']}</b>", H3))
                story.append(Paragraph(phase["desc"], SM))
                for item in phase["items"]:
                    story.append(Paragraph(
                        f"<b>Week {item['week_start']}–{item['week_end']}: "
                        f"{item['skill_name']}</b> "
                        f"({item['category']} · Gap: {item['gap']:.2f} · {item['level_required']})", BD))
                    story.append(Paragraph(
                        f"Current: {item['user_level']:.2f} → Target: {item['importance']:.2f} · "
                        f"Duration: {item['weeks']} week{'s' if item['weeks']>1 else ''}", SM))
                    story.append(Paragraph(
                        "Resources: " + " · ".join(item["resources"]), SM))
                    story.append(Spacer(1, 4))
                story.append(Spacer(1, 8))

        # ── Role Roadmap ───────────────────────────────────────────────────
        roadmap = role.get("learning_roadmap", {})
        if roadmap:
            story.append(Paragraph("Role Learning Roadmap", H3))
            for tier, label in [
                ("foundation","Foundation"),
                ("intermediate","Intermediate"),
                ("advanced","Advanced"),
            ]:
                items = roadmap.get(tier, [])
                if items:
                    story.append(Paragraph(f"<b>{label}:</b> {', '.join(items)}", BD))
            story.append(Spacer(1, 10))

        # ── Part 2: AI Predicted Roles ─────────────────────────────────────
        if ai_predictions:
            story.append(PageBreak())
            story.append(Paragraph("Part 2 — AI Career Predictions", H2))
            story.append(Paragraph(
                "The following roles were predicted by the AI model based on your full skill profile. "
                "Probability indicates the model's confidence that your skills match each role archetype.",
                BD,
            ))
            story.append(Spacer(1, 8))

            # Predicted roles table
            pred_rows = [["Rank", "Role", "Category", "Probability", "Demand", "Salary Range"]]
            for pred in ai_predictions:
                role_data = pred.get("role_data") or {}
                sal_str   = format_salary(role_data.get("salary_range", {})) if role_data else "–"
                pred_rows.append([
                    f"#{pred['rank']}",
                    pred["title"],
                    pred["category"],
                    f"{pred['probability']:.1f}%",
                    role_data.get("demand_level", "–"),
                    sal_str,
                ])
            pred_tbl = Table(pred_rows, colWidths=[1.2*cm, 5*cm, 3.5*cm, 2.5*cm, 2*cm, 3.8*cm])
            pred_tbl.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1D9E7533")),
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                ("FONTSIZE",(0,0),(-1,-1),9),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, colors.HexColor("#F0FFF8")]),
                ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#DDDDDD")),
                ("BOTTOMPADDING",(0,0),(-1,-1),5),
                ("TOPPADDING",(0,0),(-1,-1),5),
            ]))
            story += [pred_tbl, Spacer(1, 12)]

            # Role descriptions
            story.append(Paragraph("Predicted Role Summaries", H3))
            for pred in ai_predictions:
                role_data = pred.get("role_data") or {}
                story.append(Paragraph(
                    f"<b>#{pred['rank']} {pred['title']}</b> ({pred['probability']:.1f}% match)",
                    BD,
                ))
                if role_data.get("description"):
                    story.append(Paragraph(role_data["description"][:200] + "…", SM))
                tools = role_data.get("tools_and_technologies", [])
                if tools:
                    story.append(Paragraph(f"Tools: {', '.join(tools[:6])}", SM))
                story.append(Spacer(1, 6))

            # Comparison table
            story.append(Paragraph("Predicted Roles — Side by Side Comparison", H3))
            comp_rows = [["Role", "Salary Min", "Salary Max", "Growth %", "Demand"]]
            for pred in ai_predictions:
                role_data = pred.get("role_data") or {}
                sal       = role_data.get("salary_range", {})
                comp_rows.append([
                    pred["title"],
                    f"${sal.get('min',0):,.0f}",
                    f"${sal.get('max',0):,.0f}",
                    f"{role_data.get('growth_rate',0)}%",
                    role_data.get("demand_level","–"),
                ])
            comp_tbl = Table(comp_rows, colWidths=[6*cm, 3*cm, 3*cm, 2.5*cm, 2.5*cm])
            comp_tbl.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1D9E7533")),
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                ("FONTSIZE",(0,0),(-1,-1),9),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, colors.HexColor("#F0FFF8")]),
                ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#DDDDDD")),
                ("BOTTOMPADDING",(0,0),(-1,-1),5),
                ("TOPPADDING",(0,0),(-1,-1),5),
            ]))
            story += [comp_tbl, Spacer(1, 10)]

            # Highest salary and growth insights
            valid = [p for p in ai_predictions if p.get("role_data")]
            if valid:
                best_sal = max(valid, key=lambda p: p["role_data"].get("salary_range",{}).get("max",0))
                best_gr  = max(valid, key=lambda p: p["role_data"].get("growth_rate",0))
                story.append(Paragraph("Key Insights from Predicted Roles", H3))
                story.append(Paragraph(
                    f"• Highest earning potential: <b>{best_sal['title']}</b> "
                    f"(up to ${best_sal['role_data']['salary_range'].get('max',0):,.0f})", BD))
                story.append(Paragraph(
                    f"• Fastest growing: <b>{best_gr['title']}</b> "
                    f"({best_gr['role_data'].get('growth_rate',0)}% projected growth)", BD))

        # ── Footer ─────────────────────────────────────────────────────────
        # Part 3 — Career Transition
        if ct_result and isinstance(ct_result, dict):
            try:
                from_t          = ct_result.get("from_title", "")
                to_t            = ct_result.get("to_title", "")
                transferable    = ct_result.get("transferable", [])
                to_gain         = ct_result.get("to_gain", [])
                total_tw        = sum(s.get("weeks", 0) for s in to_gain)
                difficulty      = "Easy" if len(to_gain) <= 3 else "Moderate" if len(to_gain) <= 7 else "Challenging"

                story.append(PageBreak())
                story.append(Paragraph("Part 3 — Career Transition Analysis", H2))
                story += [
                    Paragraph(f"<b>From Role:</b> {from_t}", BD),
                    Paragraph(f"<b>To Role:</b> {to_t}", BD),
                    Paragraph(f"<b>Transition Difficulty:</b> {difficulty}", BD),
                    Paragraph(f"<b>Transferable Skills:</b> {len(transferable)}", BD),
                    Paragraph(f"<b>Skills to Gain:</b> {len(to_gain)}", BD),
                    Paragraph(f"<b>Estimated Time:</b> {total_tw} weeks at 8-10 hours per week", BD),
                    Spacer(1, 8),
                ]

                if to_gain:
                    story.append(Paragraph("Skills to Gain", H3))
                    gain_rows = [["Skill", "Category", "Importance", "Weeks"]]
                    for s in to_gain[:12]:
                        gain_rows.append([s.get("skill_name",""), s.get("category",""),
                                          f"{s.get('to_imp',0):.2f}", str(s.get("weeks",0))])
                    gt = Table(gain_rows, colWidths=[6*cm,4*cm,3*cm,3*cm])
                    gt.setStyle(TableStyle([
                        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E24B4A33")),
                        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                        ("FONTSIZE",(0,0),(-1,-1),9),
                        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#FFF5F5")]),
                        ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#DDDDDD")),
                        ("BOTTOMPADDING",(0,0),(-1,-1),5),("TOPPADDING",(0,0),(-1,-1),5),
                    ]))
                    story += [gt, Spacer(1,10)]

                if transferable:
                    story.append(Paragraph("Transferable Skills", H3))
                    tr_rows = [["Skill", "Category", "Current Imp.", "Target Imp."]]
                    for s in transferable[:10]:
                        tr_rows.append([s.get("skill_name",""), s.get("category",""),
                                        f"{s.get('from_imp',0):.2f}", f"{s.get('to_imp',0):.2f}"])
                    trt = Table(tr_rows, colWidths=[6*cm,4*cm,3*cm,3*cm])
                    trt.setStyle(TableStyle([
                        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1D9E7533")),
                        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                        ("FONTSIZE",(0,0),(-1,-1),9),
                        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F0FFF8")]),
                        ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#DDDDDD")),
                        ("BOTTOMPADDING",(0,0),(-1,-1),5),("TOPPADDING",(0,0),(-1,-1),5),
                    ]))
                    story += [trt, Spacer(1,10)]

                if to_gain:
                    story.append(Paragraph("Transition Learning Path", H3))
                    story.append(Paragraph(f"Week-by-week plan: {from_t} to {to_t}", BD))
                    story.append(Spacer(1,6))
                    week_counter = 1
                    for s in to_gain[:10]:
                        weeks = s.get("weeks",1)
                        story.append(Paragraph(
                            f"<b>Week {week_counter}-{week_counter+weeks-1}: "
                            f"{s.get('skill_name','')}</b> "
                            f"(Importance: {s.get('to_imp',0):.2f} · {weeks} week{'s' if weeks>1 else ''})", BD))
                        resources = s.get("resources",[])
                        if resources:
                            story.append(Paragraph("Resources: " + " · ".join(resources[:3]), SM))
                        story.append(Spacer(1,4))
                        week_counter += weeks
            except Exception as e:
                story.append(Paragraph(f"Transition data error: {str(e)}", SM))

        story += [
            Spacer(1, 20),
            HRFlowable(width="100%", thickness=0.5, color=colors.grey),
            Paragraph(
                "Generated by CareerSight: An Explainable AI-Based Career Guidance and Skill Gap Analysis System",
                SM,
            ),
        ]

        doc.build(story)
        return buf.getvalue()

    except ImportError:
        return None


def render():
    st.markdown("## Export Report")
    st.markdown(
        "Download a complete PDF report including your skill analysis, "
        "full learning path, and AI predicted career matches."
    )
    st.divider()

    roles    = sorted(load_roles(), key=lambda r: r["title"])
    role_map = {r["title"]: r for r in roles}

    # Detect saved sessions
    lp_skills  = st.session_state.get("lp_user_skills", {})
    lp_role_id = st.session_state.get("lp_role_id", "")
    lp_title   = st.session_state.get("lp_role_title", "")
    lp_plan    = st.session_state.get("lp_plan", None)
    lp_weeks   = st.session_state.get("lp_total_weeks", 0)

    sa_skills  = st.session_state.get("last_user_skills", {})
    sa_role_id = st.session_state.get("last_role_id", "")
    sa_title   = st.session_state.get("last_role_title", "")

    wi_skills  = st.session_state.get("wi_user_skills", {})
    wi_role_id = st.session_state.get("wi_role_id", "")
    wi_title   = st.session_state.get("wi_role_title", "")

    # Load predictions and enrich with fresh role_data
    raw_predictions = st.session_state.get("ai_predictions", None)
    ai_predictions  = None
    if raw_predictions:
        try:
            enriched = []
            _roles_lookup = {r["role_id"]: r for r in load_roles()}
            for p in raw_predictions:
                if isinstance(p, dict) and "role_id" in p:
                    role_data = _roles_lookup.get(p["role_id"], {})
                    enriched.append({**p, "role_data": role_data})
            ai_predictions = enriched if enriched else None
        except Exception:
            ai_predictions = None

    has_lp = bool(lp_skills and lp_role_id and lp_plan)
    has_sa = bool(sa_skills and sa_role_id)
    has_wi = bool(wi_skills and wi_role_id)

    # Source options
    source_options = []
    seen_role_ids  = set()

    if has_lp:
        source_options.append(f"Learning Path — {lp_title}")
        seen_role_ids.add(lp_role_id)

    if has_sa and sa_role_id not in seen_role_ids:
        source_options.append(f"Skill Gap Analysis — {sa_title}")
        seen_role_ids.add(sa_role_id)

    if has_wi and wi_role_id not in seen_role_ids:
        source_options.append(f"Skill Improvement Simulator — {wi_title}")
        seen_role_ids.add(wi_role_id)

    source_options.append("Choose a different role")

    st.markdown("### Step 1 — Select Skill Data Source")
    source = st.radio("Use data from:", source_options, key="exp_source")

    manual_mode = "Choose a different role" in source

    if not manual_mode:
        if "Learning Path" in source:
            active_skills, active_role_id, active_title = lp_skills, lp_role_id, lp_title
            active_plan, active_weeks = lp_plan, lp_weeks
        elif "Skill Gap Analysis" in source:
            active_skills, active_role_id, active_title = sa_skills, sa_role_id, sa_title
            active_plan, active_weeks = None, 0
        else:
            active_skills, active_role_id, active_title = wi_skills, wi_role_id, wi_title
            active_plan, active_weeks = None, 0

        role  = role_map.get(active_title, roles[0])
        rated = sum(1 for v in active_skills.values() if v > 0)
        st.success(f"Loaded: **{active_title}** — {rated} skills rated")

    else:
        col_role, col_cat = st.columns([3, 2])
        with col_cat:
            all_cats = ["All"] + sorted({r["category"] for r in roles})
            sel_cat  = st.selectbox("Filter by category", all_cats, key="exp_cat")
        with col_role:
            filtered  = roles if sel_cat == "All" else [r for r in roles if r["category"] == sel_cat]
            options   = ["— Select a role —"] + [r["title"] for r in filtered]
            sel_title = st.selectbox("Select role", options, index=0, key="exp_role")

        if sel_title == "— Select a role —":
            st.info("Select a role to continue.")
            return

        role           = role_map[sel_title]
        active_role_id = role["role_id"]
        active_title   = sel_title
        active_plan, active_weeks = None, 0

        role_skills = get_skills_for_role(active_role_id)
        role_skills = role_skills[role_skills["importance_score"] >= MIN_IMPORTANCE_THRESHOLD]
        active_skills = {}
        with st.expander("Rate your skills", expanded=True):
            for _, row in role_skills.iterrows():
                val = st.slider(row["skill_name"], 0.0, 1.0, 0.0, 0.05,
                                key=f"exp_skill_{row['skill_id']}")
                active_skills[row["skill_id"]] = val

    # AI predictions status
    st.divider()
    st.markdown("### Step 2 — AI Predictions")
    if ai_predictions:
        st.success(
            f"AI predictions loaded — top {len(ai_predictions)} predicted roles will be included in the PDF."
        )
        for p in ai_predictions:
            st.markdown(f"- **#{p['rank']} {p['title']}** — {p['probability']:.1f}% match")
    else:
        st.warning(
            "No AI predictions found. Run the **AI Career Predictor** first to include "
            "predicted roles and their comparison in the PDF. "
            "You can still export without them."
        )

    # Career transition status
    ct_result = st.session_state.get("ct_result", None)
    st.divider()
    st.markdown("### Step 3 — Career Transition")
    if ct_result and isinstance(ct_result, dict):
        from_t = ct_result.get("from_title","")
        to_t   = ct_result.get("to_title","")
        st.success(f"Career transition loaded: **{from_t} → {to_t}** will be included in the PDF.")
    else:
        st.warning("No career transition found. Run **Career Transition Analyser** to include it. You can still export without it.")

    st.divider()
    st.markdown("### PDF Contents")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.markdown("""
**Part 1 — Target Role Analysis**
- Compatibility score and match band
- Role overview — salary, demand, growth
- Full skill profile table
- Top 5 skills to learn next
- Week-by-week learning path
- Role learning roadmap
""")
    with col_p2:
        st.markdown("""
**Part 2 — AI Career Predictions**
- Top predicted roles with probability %
- Role summaries and tools
- Side by side salary & growth comparison
- Key insights from predicted roles
""")
    with col_p3:
        st.markdown("""
**Part 3 — Career Transition**
- From → To role analysis
- Transition difficulty rating
- Transferable skills table
- Skills to gain table
- Transition learning path
""")

    gen_btn = st.button(
        "Generate & Download PDF Report",
        use_container_width=True,
        type="primary",
    )
    if not gen_btn:
        return

    with st.spinner("Building your report…"):
        result   = compute_compatibility(active_skills, active_role_id)
        score    = result["score"]
        band, _  = score_to_band(score)
        top_recs = recommend_top_improvements(active_skills, active_role_id, top_n=5)

        if not active_plan:
            from views.learning_path import build_plan
            active_plan, active_weeks = build_plan(result["gaps"])

        pdf_bytes = generate_pdf(
            role_title     = active_title,
            score          = score,
            band           = band,
            role           = role,
            result         = result,
            top_recs       = top_recs,
            phases         = active_plan,
            total_weeks    = active_weeks,
            ai_predictions = ai_predictions,
            ct_result      = ct_result,
        )

    if pdf_bytes is None:
        st.error("Install reportlab:\n```\nvenv\\Scripts\\pip.exe install reportlab\n```")
        return

    filename = (
        f"CareerSight_{active_title.replace(' ','_')}_"
        f"{datetime.now().strftime('%Y%m%d')}.pdf"
    )

    st.success("Report ready!")
    col_dl, col_stats = st.columns([2, 3])
    with col_dl:
        st.download_button(
            label               = "Download PDF",
            data                = pdf_bytes,
            file_name           = filename,
            mime                = "application/pdf",
            use_container_width = True,
        )
    with col_stats:
        st.markdown(f"""
**Role:** {active_title}
**Score:** {score:.1f}% — {band}
**Strengths:** {len(result['strengths'])} · **Gaps:** {len(result['gaps'])}
**Learning phases:** {len(active_plan)} · **Total weeks:** {active_weeks}
**AI predictions included:** {"Yes — " + str(len(ai_predictions)) + " roles" if ai_predictions else "No"}
""")