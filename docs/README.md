# 📚 ADSA Project Documentation & Technical Reports

This directory houses all formal academic papers, audit dossiers, benchmark verification attestations, presentation defense guides, and automated PDF compilation pipelines for the **Entropy-Guided Hierarchical Load Balancing (ADSA P9)** project.

---

## 📁 Directory Structure

```text
docs/
├── README.md                                                          # This documentation index
├── P9.docx                                                            # Original course project proposal document
├── P9.md                                                              # Full mathematical specification & algorithms
├── PROJECT_IMPLEMENTATION.md                                          # Phase-wise implementation plan & status tracking
├── RESEARCH_PAPER.md                                                  # 8-page IEEE-format research paper manuscript
├── FINAL_PROJECT_REPORT.md                                            # Comprehensive final project report (all phases)
├── FACULTY_COMPREHENSIVE_AUDIT_DOSSIER.md                             # 6-page institutional faculty audit dossier
├── FACULTY_PRESENTATION_AND_JUSTIFICATION_GUIDE.md                   # 13-page presentation & viva defense guide
├── SPRINGER_CONFERENCE_PROCEEDINGS_GUIDE.md                           # Springer CCIS / LNCS submission compliance dossier
├── BENCHMARK_RESULTS_AND_IMPLEMENTATION_ATTESTATION.md                # Benchmark data lineage & correspondence attestation
├── DETAILED_BENCHMARK_RESULTS_AND_IMPLEMENTATION_VERIFICATION_REPORT.md # Granular benchmark & time-series audit report
│
├── pdf/                                                               # Official compiled PDF deliverables
│   ├── RESEARCH_PAPER.pdf                                             # Compiled IEEE format research paper
│   ├── FINAL_PROJECT_REPORT.pdf                                       # Compiled final project report
│   ├── SPRINGER_CONFERENCE_PROCEEDINGS_REPORT.pdf                     # Compiled 8-page Springer CCIS publication manuscript
│   ├── FACULTY_COMPREHENSIVE_AUDIT_DOSSIER.pdf                        # Compiled institutional faculty audit dossier
│   ├── FACULTY_PRESENTATION_AND_JUSTIFICATION_GUIDE.pdf                # Compiled 13-page viva presentation guide
│   ├── BENCHMARK_RESULTS_AND_IMPLEMENTATION_ATTESTATION.pdf             # Compiled benchmark attestation certificate
│   ├── DETAILED_BENCHMARK_RESULTS_AND_IMPLEMENTATION_VERIFICATION_REPORT.pdf # Granular empirical verification report
│   └── Entropy_Guided_HPC_Project_Guide.pdf                           # Course project reference guide
│
└── scripts/                                                           # Automated ReportLab PDF compilation scripts
    ├── create_paper_pdf.py                                            # Compiles RESEARCH_PAPER.pdf
    ├── create_pdf_report.py                                           # Compiles FINAL_PROJECT_REPORT.pdf
    ├── create_springer_proceedings_pdf.py                             # Compiles SPRINGER_CONFERENCE_PROCEEDINGS_REPORT.pdf
    ├── create_faculty_audit_dossier_pdf.py                            # Compiles FACULTY_COMPREHENSIVE_AUDIT_DOSSIER.pdf
    ├── create_faculty_presentation_pdf.py                             # Compiles FACULTY_PRESENTATION_AND_JUSTIFICATION_GUIDE.pdf
    ├── create_benchmark_attestation_pdf.py                            # Compiles BENCHMARK_RESULTS_AND_IMPLEMENTATION_ATTESTATION.pdf
    └── create_detailed_benchmark_report_pdf.py                        # Compiles DETAILED_BENCHMARK_RESULTS_AND_IMPLEMENTATION_VERIFICATION_REPORT.pdf
```

---

## 📄 Document Catalog

| Document (Markdown / DOCX) | Compiled PDF | Target Audience & Purpose |
|:---|:---|:---|
| [`P9.md`](./P9.md) | — | Mathematical foundations, dual entropy formulations, $O(\log N)$ tree proofs, 15 IEEE citations. |
| [`PROJECT_IMPLEMENTATION.md`](./PROJECT_IMPLEMENTATION.md) | — | Phase-by-phase implementation tracking (Phase 1–4) and technical roadmap. |
| [`RESEARCH_PAPER.md`](./RESEARCH_PAPER.md) | [`RESEARCH_PAPER.pdf`](./pdf/RESEARCH_PAPER.pdf) | IEEE Transactions format manuscript with empirical results, tables, and architecture diagrams. |
| [`FINAL_PROJECT_REPORT.md`](./FINAL_PROJECT_REPORT.md) | [`FINAL_PROJECT_REPORT.pdf`](./pdf/FINAL_PROJECT_REPORT.pdf) | Comprehensive 6-page institutional final report detailing the complete project lifecycle. |
| [`SPRINGER_CONFERENCE_PROCEEDINGS_GUIDE.md`](./SPRINGER_CONFERENCE_PROCEEDINGS_GUIDE.md) | [`SPRINGER_CONFERENCE_PROCEEDINGS_REPORT.pdf`](./pdf/SPRINGER_CONFERENCE_PROCEEDINGS_REPORT.pdf) | 8-page Springer CCIS / LNCS author accepted manuscript with running headers and Springer geometry. |
| [`FACULTY_COMPREHENSIVE_AUDIT_DOSSIER.md`](./FACULTY_COMPREHENSIVE_AUDIT_DOSSIER.md) | [`FACULTY_COMPREHENSIVE_AUDIT_DOSSIER.pdf`](./pdf/FACULTY_COMPREHENSIVE_AUDIT_DOSSIER.pdf) | 6-page comprehensive audit verifying 100% compliance across all evaluation rubrics for 'O' grade. |
| [`FACULTY_PRESENTATION_AND_JUSTIFICATION_GUIDE.md`](./FACULTY_PRESENTATION_AND_JUSTIFICATION_GUIDE.md) | [`FACULTY_PRESENTATION_AND_JUSTIFICATION_GUIDE.pdf`](./pdf/FACULTY_PRESENTATION_AND_JUSTIFICATION_GUIDE.pdf) | 13-page oral defense preparation guide covering slide scripts, live demo protocols, and examiner Q&A. |
| [`BENCHMARK_RESULTS_AND_IMPLEMENTATION_ATTESTATION.md`](./BENCHMARK_RESULTS_AND_IMPLEMENTATION_ATTESTATION.md) | [`BENCHMARK_RESULTS_AND_IMPLEMENTATION_ATTESTATION.pdf`](./pdf/BENCHMARK_RESULTS_AND_IMPLEMENTATION_ATTESTATION.pdf) | Signed data lineage certification linking `benchmark_results.json` directly to the codebase. |
| [`DETAILED_BENCHMARK_RESULTS_AND_IMPLEMENTATION_VERIFICATION_REPORT.md`](./DETAILED_BENCHMARK_RESULTS_AND_IMPLEMENTATION_VERIFICATION_REPORT.md) | [`DETAILED_BENCHMARK_RESULTS_AND_IMPLEMENTATION_VERIFICATION_REPORT.pdf`](./pdf/DETAILED_BENCHMARK_RESULTS_AND_IMPLEMENTATION_VERIFICATION_REPORT.pdf) | Deep empirical audit examining multi-trace cross-validation (LANL, LLNL, CEA Curie) and time-series data. |

---

## 🛠️ Recompiling PDF Reports

All PDFs are programmatically generated using Python and ReportLab. To recompile any PDF deliverable, run the corresponding script inside `docs/scripts/`:

```bash
# Recompile individual documents
python docs/scripts/create_paper_pdf.py
python docs/scripts/create_pdf_report.py
python docs/scripts/create_springer_proceedings_pdf.py
python docs/scripts/create_faculty_audit_dossier_pdf.py
python docs/scripts/create_faculty_presentation_pdf.py
python docs/scripts/create_benchmark_attestation_pdf.py
python docs/scripts/create_detailed_benchmark_report_pdf.py
```

All compiled PDFs will automatically be placed into [`docs/pdf/`](./pdf/).
