"""Module for testing FUSOR Translators"""

import pickle
from pathlib import Path

import polars as pl
import pytest
from cool_seq_tool.schemas import Assembly, CoordinateType

from fusor.fusion_caller_models import (
    CIVIC,
    JAFFA,
    Arriba,
    Cicero,
    EnFusion,
    FusionCatcher,
    Genie,
    STARFusion,
)
from fusor.models import (
    AnchoredReads,
    AssayedFusion,
    BreakpointCoverage,
    CategoricalFusion,
    ContigSequence,
    ReadData,
    SpanningReads,
    SplitReads,
    UnknownGeneElement,
)
from fusor.translator import (
    ArribaTranslator,
    CiceroTranslator,
    CIVICTranslator,
    EnFusionTranslator,
    FusionCatcherTranslator,
    FusionMapTranslator,
    GenieTranslator,
    JAFFATranslator,
    MOATranslator,
    STARFusionTranslator,
)


@pytest.fixture(scope="module")
def fusion_data_example():
    """Create example assayed fusion for TPM3::PDGFRB with exonic breakpoints"""

    def _create_base_fixture(**kwargs):
        params = {
            "type": "AssayedFusion",
            "structure": [
                {
                    "type": "TranscriptSegmentElement",
                    "transcript": "refseq:NM_152263.4",
                    "strand": -1,
                    "exonEnd": 8,
                    "exonEndOffset": -66,
                    "gene": {
                        "primaryCoding": {
                            "id": "hgnc:12012",
                            "code": "HGNC:12012",
                            "system": "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/",
                        },
                        "conceptType": "Gene",
                        "name": "TPM3",
                    },
                    "elementGenomicEnd": {
                        "id": "ga4gh:SL.6lXn5i3zqcZUfmtBSieTiVL4Nt2gPGKY",
                        "type": "SequenceLocation",
                        "digest": "6lXn5i3zqcZUfmtBSieTiVL4Nt2gPGKY",
                        "sequenceReference": {
                            "id": "refseq:NC_000001.11",
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.Ya6Rs7DHhDeg7YaOSg1EoNi3U_nQ9SvO",
                        },
                        "start": 154170465,
                    },
                },
                {
                    "type": "TranscriptSegmentElement",
                    "transcript": "refseq:NM_002609.4",
                    "strand": -1,
                    "exonStart": 11,
                    "exonStartOffset": 2,
                    "gene": {
                        "primaryCoding": {
                            "id": "hgnc:8804",
                            "code": "HGNC:8804",
                            "system": "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/",
                        },
                        "conceptType": "Gene",
                        "name": "PDGFRB",
                    },
                    "elementGenomicStart": {
                        "id": "ga4gh:SL.Sp1lwuHbRCkWIoe4zzwVKPsS8zK8i0ck",
                        "type": "SequenceLocation",
                        "digest": "Sp1lwuHbRCkWIoe4zzwVKPsS8zK8i0ck",
                        "sequenceReference": {
                            "id": "refseq:NC_000005.10",
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.aUiQCzCPZ2d0csHbMSbh2NzInhonSXwI",
                        },
                        "end": 150126612,
                    },
                },
            ],
            "causativeEvent": {"type": "CausativeEvent", "eventType": "rearrangement"},
            "r_frame_preserved": True,
            "assay": None,
            "viccNomenclature": "NM_152263.4(TPM3):e.8-66::NM_002609.4(PDGFRB):e.11+2",
        }
        assayed_fusion = AssayedFusion(**params)
        return assayed_fusion.model_copy(update=kwargs)

    return _create_base_fixture


@pytest.fixture(scope="module")
def fusion_data_example_nonexonic():
    """Create example assayed fusion for TPM3::PDGFRB with non-exonic breakpoints"""

    def _create_base_fixture(**kwargs):
        params = {
            "type": "AssayedFusion",
            "structure": [
                {
                    "type": "TranscriptSegmentElement",
                    "transcript": "refseq:NM_152263.4",
                    "strand": -1,
                    "exonEnd": 4,
                    "exonEndOffset": 5,
                    "gene": {
                        "primaryCoding": {
                            "id": "hgnc:12012",
                            "code": "HGNC:12012",
                            "system": "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/",
                        },
                        "conceptType": "Gene",
                        "name": "TPM3",
                    },
                    "elementGenomicEnd": {
                        "id": "ga4gh:SL.O1rVKQA2FTdy_FFWg3qJVSTG_TF_Mkex",
                        "type": "SequenceLocation",
                        "digest": "O1rVKQA2FTdy_FFWg3qJVSTG_TF_Mkex",
                        "sequenceReference": {
                            "id": "refseq:NC_000001.11",
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.Ya6Rs7DHhDeg7YaOSg1EoNi3U_nQ9SvO",
                        },
                        "start": 154173078,
                    },
                },
                {
                    "type": "TranscriptSegmentElement",
                    "transcript": "refseq:NM_002609.4",
                    "strand": -1,
                    "exonStart": 11,
                    "exonStartOffset": -559,
                    "gene": {
                        "primaryCoding": {
                            "id": "hgnc:8804",
                            "code": "HGNC:8804",
                            "system": "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/",
                        },
                        "conceptType": "Gene",
                        "name": "PDGFRB",
                    },
                    "elementGenomicStart": {
                        "id": "ga4gh:SL.GtoWMuox4tOyX2I5L9Baobnpgc1pDIVJ",
                        "type": "SequenceLocation",
                        "digest": "GtoWMuox4tOyX2I5L9Baobnpgc1pDIVJ",
                        "sequenceReference": {
                            "id": "refseq:NC_000005.10",
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.aUiQCzCPZ2d0csHbMSbh2NzInhonSXwI",
                        },
                        "end": 150127173,
                    },
                },
            ],
            "causativeEvent": {"type": "CausativeEvent", "eventType": "rearrangement"},
            "r_frame_preserved": True,
            "assay": None,
            "viccNomenclature": "NM_152263.4(TPM3):e.4+5::NM_002609.4(PDGFRB):e.11-559",
        }
        assayed_fusion = AssayedFusion(**params)
        return assayed_fusion.model_copy(update=kwargs)

    return _create_base_fixture


@pytest.fixture(scope="module")
def fusion_data_example_categorical():
    """Create test fixture for CategoricalFusion object with BCR::ABL1 fusion"""

    def _create_base_fixture(**kwargs):
        params = {
            "type": "CategoricalFusion",
            "structure": [
                {
                    "type": "TranscriptSegmentElement",
                    "transcript": "refseq:NM_004327.4",
                    "strand": 1,
                    "exonEnd": 14,
                    "exonEndOffset": 0,
                    "gene": {
                        "primaryCoding": {
                            "id": "hgnc:1014",
                            "code": "HGNC:1014",
                            "system": "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/",
                        },
                        "conceptType": "Gene",
                        "name": "BCR",
                    },
                    "elementGenomicEnd": {
                        "id": "ga4gh:SL.wgMvqEhsH2IB1bQFlCxl-eD3A588MO8d",
                        "type": "SequenceLocation",
                        "digest": "wgMvqEhsH2IB1bQFlCxl-eD3A588MO8d",
                        "sequenceReference": {
                            "id": "refseq:NC_000022.11",
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.7B7SHsmchAR0dFcDCuSFjJAo7tX87krQ",
                        },
                        "end": 23290413,
                    },
                },
                {
                    "type": "TranscriptSegmentElement",
                    "transcript": "refseq:NM_005157.6",
                    "strand": 1,
                    "exonStart": 2,
                    "exonStartOffset": 0,
                    "gene": {
                        "primaryCoding": {
                            "id": "hgnc:76",
                            "code": "HGNC:76",
                            "system": "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/",
                        },
                        "conceptType": "Gene",
                        "name": "ABL1",
                    },
                    "elementGenomicStart": {
                        "id": "ga4gh:SL.GvvCD7Y-_598-ZP4yNGiPa1aPL-kofY6",
                        "type": "SequenceLocation",
                        "digest": "GvvCD7Y-_598-ZP4yNGiPa1aPL-kofY6",
                        "sequenceReference": {
                            "id": "refseq:NC_000009.12",
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.KEO-4XBcm1cxeo_DIQ8_ofqGUkp4iZhI",
                        },
                        "start": 130854063,
                    },
                },
            ],
            "viccNomenclature": "NM_004327.4(BCR):e.14::NM_005157.6(ABL1):e.2",
        }
        categorical_fusion = CategoricalFusion(**params)
        return categorical_fusion.model_copy(update=kwargs)

    return _create_base_fixture


@pytest.fixture(scope="module")
def fusion_data_example_categorical_mpge():
    """Create test fixture for CategoricalFusion where one partner is a MultiplePossibleGenesElement object"""

    def _create_base_fixture(**kwargs):
        params = {
            "type": "CategoricalFusion",
            "structure": [
                {
                    "type": "MultiplePossibleGenesElement",
                },
                {
                    "type": "TranscriptSegmentElement",
                    "transcript": "refseq:NM_002529.4",
                    "strand": 1,
                    "exonStart": 9,
                    "exonStartOffset": 0,
                    "gene": {
                        "primaryCoding": {
                            "id": "hgnc:8031",
                            "code": "HGNC:8031",
                            "system": "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/",
                        },
                        "conceptType": "Gene",
                        "name": "NTRK1",
                    },
                    "elementGenomicStart": {
                        "id": "ga4gh:SL.ndqfSqOGncba6_XTbtJM9aFeV-0fwr13",
                        "type": "SequenceLocation",
                        "digest": "ndqfSqOGncba6_XTbtJM9aFeV-0fwr13",
                        "sequenceReference": {
                            "id": "refseq:NC_000001.11",
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.Ya6Rs7DHhDeg7YaOSg1EoNi3U_nQ9SvO",
                        },
                        "start": 156874382,
                    },
                },
            ],
            "viccNomenclature": "v::NM_002529.4(NTRK1):e.9",
        }
        categorical_fusion = CategoricalFusion(**params)
        return categorical_fusion.model_copy(update=kwargs)

    return _create_base_fixture


@pytest.fixture(scope="module")
def fusion_data_example_categorical_nonzerooffset():
    """Create test fixture for CategoricalFusion where the offset is non-zero"""

    def _create_base_fixture(**kwargs):
        params = {
            "type": "CategoricalFusion",
            "structure": [
                {
                    "type": "TranscriptSegmentElement",
                    "transcript": "refseq:NM_005252.4",
                    "strand": 1,
                    "exonEnd": 4,
                    "exonEndOffset": -1122,
                    "gene": {
                        "primaryCoding": {
                            "id": "hgnc:3796",
                            "code": "HGNC:3796",
                            "system": "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/",
                        },
                        "conceptType": "Gene",
                        "name": "FOS",
                    },
                    "elementGenomicEnd": {
                        "id": "ga4gh:SL.dWC0LMlSNxmqC1J0_-GTQtXFhH7vjnoG",
                        "type": "SequenceLocation",
                        "digest": "dWC0LMlSNxmqC1J0_-GTQtXFhH7vjnoG",
                        "sequenceReference": {
                            "id": "refseq:NC_000014.9",
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.eK4D2MosgK_ivBkgi6FVPg5UXs1bYESm",
                        },
                        "end": 75281108,
                    },
                },
                {
                    "type": "MultiplePossibleGenesElement",
                },
            ],
            "viccNomenclature": "NM_005252.4(FOS):e.4-1122::v",
        }
        categorical_fusion = CategoricalFusion(**params)
        return categorical_fusion.model_copy(update=kwargs)

    return _create_base_fixture


@pytest.mark.asyncio
async def test_jaffa(
    fusion_data_example, fusion_data_example_nonexonic, fusor_instance
):
    """Test JAFFA translator"""
    translator = JAFFATranslator(fusor=fusor_instance)
    # Test exonic breakpoint
    jaffa = JAFFA(
        fusion_genes="TPM3:PDGFRB",
        chrom1="chr1",
        base1=154170465,
        chrom2="chr5",
        base2=150126612,
        rearrangement=True,
        classification="HighConfidence",
        inframe=True,
        spanning_reads=100,
        spanning_pairs=80,
    )

    jaffa_fusor = await translator.translate(
        jaffa,
        CoordinateType.INTER_RESIDUE.value,
        Assembly.GRCH38.value,
    )
    fusion_data_example = fusion_data_example(
        readData=ReadData(
            split=SplitReads(splitReads=100), spanning=SpanningReads(spanningReads=80)
        )
    )
    assert jaffa_fusor.structure == fusion_data_example.structure
    assert jaffa_fusor.readData == fusion_data_example.readData
    assert jaffa_fusor.viccNomenclature == fusion_data_example.viccNomenclature

    # Test non-exonic breakpoint
    jaffa.base1 = 154173079
    jaffa.base2 = 150127173

    jaffa_fusor_nonexonic = await translator.translate(
        jaffa,
        CoordinateType.RESIDUE.value,
        Assembly.GRCH38.value,
    )
    fusion_data_example_nonexonic = fusion_data_example_nonexonic(
        readData=ReadData(
            split=SplitReads(splitReads=100), spanning=SpanningReads(spanningReads=80)
        )
    )
    assert jaffa_fusor_nonexonic.structure == fusion_data_example_nonexonic.structure
    assert jaffa_fusor_nonexonic.readData == fusion_data_example_nonexonic.readData
    assert (
        jaffa_fusor_nonexonic.viccNomenclature
        == fusion_data_example_nonexonic.viccNomenclature
    )

    # Test unknown partner
    jaffa.fusion_genes = "NA:PDGFRB"
    jaffa_fusor_unknown = await translator.translate(
        jaffa, CoordinateType.RESIDUE.value, Assembly.GRCH38.value
    )
    assert jaffa_fusor_unknown.structure[0] == UnknownGeneElement()
    assert jaffa_fusor_unknown.viccNomenclature == "?::NM_002609.4(PDGFRB):e.11-559"
    jaffa.fusion_genes = "TPM3:NA"
    jaffa_fusor_unknown = await translator.translate(
        jaffa, CoordinateType.RESIDUE.value, Assembly.GRCH38.value
    )
    assert jaffa_fusor_unknown.structure[1] == UnknownGeneElement()
    assert jaffa_fusor_unknown.viccNomenclature == "NM_152263.4(TPM3):e.4+5::?"


@pytest.mark.asyncio
async def test_star_fusion(
    fusion_data_example, fusion_data_example_nonexonic, fusor_instance
):
    """Test STAR-Fusion translator"""
    translator = STARFusionTranslator(fusor=fusor_instance)
    # Test exonic breakpoints
    star_fusion = STARFusion(
        left_gene="TPM3^ENSG00000143549.19",
        right_gene="PDGFRB^ENSG00000113721",
        left_breakpoint="chr1:154170465:-",
        right_breakpoint="chr5:150126612:-",
        annots='["INTERCHROMOSOMAL]',
        junction_read_count=100,
        spanning_frag_count=80,
    )

    star_fusion_fusor = await translator.translate(
        star_fusion,
        CoordinateType.INTER_RESIDUE.value,
        Assembly.GRCH38.value,
    )
    fusion_data_example = fusion_data_example(
        readData=ReadData(
            split=SplitReads(splitReads=100), spanning=SpanningReads(spanningReads=80)
        )
    )
    assert star_fusion_fusor.structure == fusion_data_example.structure
    assert star_fusion_fusor.readData == fusion_data_example.readData
    assert star_fusion_fusor.viccNomenclature == fusion_data_example.viccNomenclature

    # Test non-exonic breakpoints
    star_fusion.left_breakpoint = "chr1:154173079:-"
    star_fusion.right_breakpoint = "chr5:150127173:-"

    star_fusion_fusor_nonexonic = await translator.translate(
        star_fusion,
        CoordinateType.RESIDUE.value,
        Assembly.GRCH38.value,
    )
    fusion_data_example_nonexonic = fusion_data_example_nonexonic(
        readData=ReadData(
            split=SplitReads(splitReads=100), spanning=SpanningReads(spanningReads=80)
        )
    )
    assert (
        star_fusion_fusor_nonexonic.structure == fusion_data_example_nonexonic.structure
    )
    assert (
        star_fusion_fusor_nonexonic.readData == fusion_data_example_nonexonic.readData
    )
    assert (
        star_fusion_fusor_nonexonic.viccNomenclature
        == fusion_data_example_nonexonic.viccNomenclature
    )

    # Test unknown partners
    star_fusion.left_gene = "NA"
    star_fusion_fusor_unknown = await translator.translate(
        star_fusion,
        CoordinateType.INTER_RESIDUE.value,
        Assembly.GRCH38.value,
    )
    assert star_fusion_fusor_unknown.structure[0] == UnknownGeneElement()
    assert (
        star_fusion_fusor_unknown.viccNomenclature == "?::NM_002609.4(PDGFRB):e.11-559"
    )
    star_fusion.left_gene = "TPM3"
    star_fusion.right_gene = "NA"
    star_fusion_fusor_unknown = await translator.translate(
        star_fusion,
        CoordinateType.INTER_RESIDUE.value,
        Assembly.GRCH38.value,
    )
    assert star_fusion_fusor_unknown.structure[1] == UnknownGeneElement()
    assert star_fusion_fusor_unknown.viccNomenclature == "NM_152263.4(TPM3):e.4+4::?"


@pytest.mark.asyncio
async def test_fusion_catcher(
    fusion_data_example, fusion_data_example_nonexonic, fusor_instance
):
    """Test Fusion Catcher translator"""
    translator = FusionCatcherTranslator(fusor=fusor_instance)
    # Test exonic breakpoint
    fusion_catcher = FusionCatcher(
        five_prime_partner="TPM3",
        three_prime_partner="PDGFRB",
        five_prime_fusion_point="1:154170465:-",
        three_prime_fusion_point="5:150126612:-",
        predicted_effect="exonic(no-known-CDS)/exonic(no-known-CDS)",
        spanning_unique_reads=100,
        spanning_reads=80,
        fusion_sequence="CTAGATGAC*TACTACTA",
    )

    fusion_catcher_fusor = await translator.translate(
        fusion_catcher,
        CoordinateType.INTER_RESIDUE.value,
        Assembly.GRCH38.value,
    )
    fusion_data_example = fusion_data_example(
        readData=ReadData(
            split=SplitReads(splitReads=100), spanning=SpanningReads(spanningReads=80)
        ),
        contig=ContigSequence(contig="CTAGATGAC*TACTACTA"),
    )
    assert fusion_catcher_fusor.structure == fusion_data_example.structure
    assert fusion_catcher_fusor.readData == fusion_data_example.readData
    assert fusion_catcher_fusor.contig == fusion_catcher_fusor.contig
    assert (
        fusion_catcher_fusor.viccNomenclature == fusion_catcher_fusor.viccNomenclature
    )

    # Test non-exonic breakpoints
    fusion_catcher.five_prime_fusion_point = "1:154173079:-"
    fusion_catcher.three_prime_fusion_point = "5:150127173:-"

    fusion_catcher_fusor_nonexonic = await translator.translate(
        fusion_catcher,
        CoordinateType.RESIDUE.value,
        Assembly.GRCH38.value,
    )
    fusion_data_example_nonexonic = fusion_data_example_nonexonic(
        readData=ReadData(
            split=SplitReads(splitReads=100), spanning=SpanningReads(spanningReads=80)
        ),
        contig=ContigSequence(contig="CTAGATGAC*TACTACTA"),
    )
    assert (
        fusion_catcher_fusor_nonexonic.structure
        == fusion_data_example_nonexonic.structure
    )
    assert (
        fusion_catcher_fusor_nonexonic.readData
        == fusion_data_example_nonexonic.readData
    )
    assert fusion_catcher_fusor_nonexonic.contig == fusion_data_example_nonexonic.contig
    assert (
        fusion_catcher_fusor_nonexonic.viccNomenclature
        == fusion_catcher_fusor_nonexonic.viccNomenclature
    )

    # Test unknown partners
    fusion_catcher.five_prime_partner = "NA"
    fusion_catcher_fusor_unknown = await translator.translate(
        fusion_catcher, CoordinateType.RESIDUE.value, Assembly.GRCH38.value
    )
    assert fusion_catcher_fusor_unknown.structure[0] == UnknownGeneElement()
    assert (
        fusion_catcher_fusor_unknown.viccNomenclature
        == "?::NM_002609.4(PDGFRB):e.11-559"
    )
    fusion_catcher.five_prime_partner = "TPM3"
    fusion_catcher.three_prime_partner = "NA"
    fusion_catcher_fusor_unknown = await translator.translate(
        fusion_catcher, CoordinateType.RESIDUE.value, Assembly.GRCH38.value
    )
    assert fusion_catcher_fusor_unknown.structure[1] == UnknownGeneElement()
    assert fusion_catcher_fusor_unknown.viccNomenclature == "NM_152263.4(TPM3):e.4+5::?"


@pytest.mark.asyncio
async def test_fusion_map(
    fusion_data_example, fusion_data_example_nonexonic, fusor_instance
):
    """Test Fusion Map translator"""
    translator = FusionMapTranslator(fusor=fusor_instance)
    # Test exonic breakpoint
    fusion_map_data = pl.DataFrame(
        {
            "KnownGene1": "TPM3",
            "KnownGene2": "PDGFRB",
            "Chromosome1": "1",
            "Position1": "154170465",
            "Chromosome2": "5",
            "Position2": "150126612",
            "FusionGene": "TPM3->PDGFRB",
            "SplicePatternClass": "CanonicalPattern[Major]",
            "FrameShiftClass": "InFrame",
        }
    )
    fusion_map_fusor = await translator.translate(
        fusion_map_data, CoordinateType.INTER_RESIDUE.value, Assembly.GRCH38.value
    )
    assert fusion_map_fusor.structure == fusion_data_example().structure

    # Test non-exonic breakpoint
    fusion_map_data_nonexonic = pl.DataFrame(
        {
            "KnownGene1": "TPM3",
            "KnownGene2": "PDGFRB",
            "Chromosome1": "1",
            "Position1": "154173079",
            "Chromosome2": "5",
            "Position2": "150127173",
            "FusionGene": "TPM3->PDGFRB",
            "SplicePatternClass": "CanonicalPattern[Major]",
            "FrameShiftClass": "InFrame",
        }
    )
    fusion_map_fusor_nonexonic = await translator.translate(
        fusion_map_data_nonexonic, CoordinateType.RESIDUE.value, Assembly.GRCH38.value
    )
    assert (
        fusion_map_fusor_nonexonic.structure
        == fusion_data_example_nonexonic().structure
    )


@pytest.mark.asyncio
async def test_arriba(
    fusion_data_example, fusion_data_example_nonexonic, fusor_instance
):
    """Test Arriba translator"""
    translator = ArribaTranslator(fusor=fusor_instance)
    # Test exonic breakpoint
    arriba = Arriba(
        gene1="TPM3",
        gene2="PDGFRB",
        strand1="-/-",
        strand2="-/-",
        breakpoint1="1:154170465",
        breakpoint2="5:150126612",
        event_type="translocation",
        confidence="high",
        direction1="upstream",
        direction2="downstream",
        rf="in-frame",
        split_reads1=100,
        split_reads2=95,
        discordant_mates=30,
        coverage1=200,
        coverage2=190,
        fusion_transcript="CTAGATGAC_TACTACTA|GTACTACT",
    )

    arriba_fusor = await translator.translate(
        arriba,
        CoordinateType.INTER_RESIDUE.value,
        Assembly.GRCH38.value,
    )
    fusion_data_example = fusion_data_example(
        readData=ReadData(spanning=SpanningReads(spanningReads=30)),
        contig=ContigSequence(contig=arriba.fusion_transcript),
    )
    fusion_data_example.structure[0].coverage = BreakpointCoverage(fragmentCoverage=200)
    fusion_data_example.structure[0].anchoredReads = AnchoredReads(reads=100)
    fusion_data_example.structure[1].coverage = BreakpointCoverage(fragmentCoverage=190)
    fusion_data_example.structure[1].anchoredReads = AnchoredReads(reads=95)
    assert arriba_fusor.structure == fusion_data_example.structure
    assert arriba_fusor.readData == fusion_data_example.readData
    assert arriba_fusor.contig == fusion_data_example.contig
    assert arriba_fusor.viccNomenclature == fusion_data_example.viccNomenclature

    # Test non-exonic breakpoint
    arriba.breakpoint1 = "1:154173079"
    arriba.breakpoint2 = "5:150127173"

    arriba_fusor_nonexonic = await translator.translate(
        arriba,
        CoordinateType.RESIDUE.value,
        Assembly.GRCH38.value,
    )
    fusion_data_example_nonexonic = fusion_data_example_nonexonic(
        readData=ReadData(spanning=SpanningReads(spanningReads=30)),
        contig=ContigSequence(contig=arriba.fusion_transcript),
    )
    fusion_data_example_nonexonic.structure[0].coverage = BreakpointCoverage(
        fragmentCoverage=200
    )
    fusion_data_example_nonexonic.structure[0].anchoredReads = AnchoredReads(reads=100)
    fusion_data_example_nonexonic.structure[1].coverage = BreakpointCoverage(
        fragmentCoverage=190
    )
    fusion_data_example_nonexonic.structure[1].anchoredReads = AnchoredReads(reads=95)
    assert arriba_fusor_nonexonic.structure == fusion_data_example_nonexonic.structure
    assert arriba_fusor_nonexonic.readData == fusion_data_example_nonexonic.readData
    assert arriba_fusor_nonexonic.contig == fusion_data_example_nonexonic.contig
    assert (
        arriba_fusor_nonexonic.viccNomenclature
        == fusion_data_example_nonexonic.viccNomenclature
    )

    # Test Linker Sequence
    arriba_linker = arriba.model_copy(deep=True)
    arriba_linker.fusion_transcript = "ATAGAT|atatacgat|TATGAT"
    arriba_fusor_linker = await translator.translate(
        arriba_linker, CoordinateType.RESIDUE.value, Assembly.GRCH38.value
    )
    linker_element = arriba_fusor_linker.structure[1]
    assert linker_element
    assert linker_element.linkerSequence.sequence.root == "ATATACGAT"
    assert (
        arriba_fusor_linker.viccNomenclature
        == "NM_152263.4(TPM3):e.4+5::ATATACGAT::NM_002609.4(PDGFRB):e.11-559"
    )

    # Test unknown partners
    arriba.gene1 = "NA"
    arriba_fusor_unknown = await translator.translate(
        arriba, CoordinateType.RESIDUE.value, Assembly.GRCH38.value
    )
    assert arriba_fusor_unknown.structure[0] == UnknownGeneElement()
    assert arriba_fusor_unknown.viccNomenclature == "?::NM_002609.4(PDGFRB):e.11-559"
    arriba.gene1 = "TPM3"
    arriba.gene2 = "NA"
    arriba_fusor_unknown = await translator.translate(
        arriba, CoordinateType.RESIDUE.value, Assembly.GRCH38.value
    )
    assert arriba_fusor_unknown.structure[1] == UnknownGeneElement()
    assert arriba_fusor_unknown.viccNomenclature == "NM_152263.4(TPM3):e.4+5::?"


@pytest.mark.asyncio
async def test_cicero(
    fusion_data_example, fusion_data_example_nonexonic, fusor_instance
):
    """Test CICERO translator"""
    translator = CiceroTranslator(fusor=fusor_instance)
    # Test exonic breakpoint
    cicero = Cicero(
        gene_5prime="TPM3",
        gene_3prime="PDGFRB",
        chr_5prime="1",
        chr_3prime="5",
        pos_5prime=154170466,
        pos_3prime=150126612,
        sv_ort=">",
        event_type="CTX",
        reads_5prime=100,
        reads_3prime=90,
        coverage_5prime=200,
        coverage_3prime=190,
        contig="ATCATACTAGATACTACTACGATGAGAGAGTACATAGAT",
    )

    cicero_fusor = await translator.translate(
        cicero,
        CoordinateType.RESIDUE.value,
        Assembly.GRCH38.value,
    )
    fusion_data_example = fusion_data_example(
        contig=ContigSequence(contig=cicero.contig)
    )
    fusion_data_example.structure[0].coverage = BreakpointCoverage(fragmentCoverage=200)
    fusion_data_example.structure[0].anchoredReads = AnchoredReads(reads=100)
    fusion_data_example.structure[1].coverage = BreakpointCoverage(fragmentCoverage=190)
    fusion_data_example.structure[1].anchoredReads = AnchoredReads(reads=90)
    assert cicero_fusor.structure == fusion_data_example.structure
    assert cicero_fusor.readData == fusion_data_example.readData
    assert cicero_fusor.contig == fusion_data_example.contig
    assert cicero_fusor.viccNomenclature == fusion_data_example.viccNomenclature

    # Test non-exonic breakpoint
    cicero.pos_5prime = 154173079
    cicero.pos_3prime = 150127173

    cicero_fusor_nonexonic = await translator.translate(
        cicero,
        CoordinateType.RESIDUE.value,
        Assembly.GRCH38.value,
    )
    fusion_data_example_nonexonic = fusion_data_example_nonexonic(
        contig=ContigSequence(contig=cicero.contig)
    )
    fusion_data_example_nonexonic.structure[0].coverage = BreakpointCoverage(
        fragmentCoverage=200
    )
    fusion_data_example_nonexonic.structure[0].anchoredReads = AnchoredReads(reads=100)
    fusion_data_example_nonexonic.structure[1].coverage = BreakpointCoverage(
        fragmentCoverage=190
    )
    fusion_data_example_nonexonic.structure[1].anchoredReads = AnchoredReads(reads=90)
    assert cicero_fusor_nonexonic.structure == fusion_data_example_nonexonic.structure
    assert cicero_fusor_nonexonic.readData == fusion_data_example_nonexonic.readData
    assert cicero_fusor_nonexonic.contig == fusion_data_example_nonexonic.contig
    assert (
        cicero_fusor_nonexonic.viccNomenclature
        == cicero_fusor_nonexonic.viccNomenclature
    )

    # Test case where the called fusion does not have confident biological meaning
    cicero.sv_ort = "?"

    non_confident_bio = await translator.translate(
        cicero,
        CoordinateType.RESIDUE.value,
        Assembly.GRCH38.value,
    )
    assert (
        non_confident_bio
        == "CICERO annotation indicates that this event does not have confident biological meaning"
    )

    # Test case where multiple gene symbols are reported for a fusion partner
    cicero.gene_3prime = "PDGFRB,PDGFRB-FGFR4,FGFR4"

    multiple_genes_fusion_partner = await translator.translate(
        cicero,
        CoordinateType.RESIDUE.value,
        Assembly.GRCH38.value,
    )
    assert (
        multiple_genes_fusion_partner
        == "Ambiguous gene symbols are reported by CICERO for at least one of the fusion partners"
    )

    # Test unknown partners
    cicero.sv_ort = ">"
    cicero.gene_5prime = "NA"
    cicero.gene_3prime = "PDGFRB"
    cicero_fusor_unknown = await translator.translate(
        cicero, CoordinateType.RESIDUE.value, Assembly.GRCH38.value
    )
    assert cicero_fusor_unknown.viccNomenclature == "?::NM_002609.4(PDGFRB):e.11-559"
    assert cicero_fusor_unknown.structure[0] == UnknownGeneElement()
    cicero.gene_5prime = "TPM3"
    cicero.gene_3prime = "NA"
    cicero_fusor_unknown = await translator.translate(
        cicero, CoordinateType.RESIDUE.value, Assembly.GRCH38.value
    )
    assert cicero_fusor_unknown.structure[1] == UnknownGeneElement()
    assert cicero_fusor_unknown.viccNomenclature == "NM_152263.4(TPM3):e.4+5::?"


@pytest.mark.asyncio
async def test_enfusion(
    fusion_data_example, fusion_data_example_nonexonic, fusor_instance
):
    """Test EnFusion translator"""
    translator = EnFusionTranslator(fusor=fusor_instance)
    # Test exonic breakpoint
    enfusion = EnFusion(
        gene_5prime="TPM3",
        gene_3prime="PDGFRB",
        chr_5prime=1,
        chr_3prime=5,
        break_5prime=154170465,
        break_3prime=150126612,
    )

    enfusion_fusor = await translator.translate(
        enfusion,
        CoordinateType.INTER_RESIDUE.value,
        Assembly.GRCH38.value,
    )
    assert enfusion_fusor.structure == fusion_data_example().structure
    assert enfusion_fusor.viccNomenclature == fusion_data_example().viccNomenclature

    # Test non-exonic breakpoint
    enfusion.break_5prime = 154173079
    enfusion.break_3prime = 150127173

    enfusion_fusor_nonexonic = await translator.translate(
        enfusion,
        CoordinateType.RESIDUE.value,
        Assembly.GRCH38.value,
    )
    assert (
        enfusion_fusor_nonexonic.structure == fusion_data_example_nonexonic().structure
    )
    assert (
        enfusion_fusor_nonexonic.viccNomenclature
        == fusion_data_example_nonexonic().viccNomenclature
    )

    # Test unknown partner
    enfusion.gene_5prime = "NA"
    enfusion_fusor_unknown = await translator.translate(
        enfusion, CoordinateType.RESIDUE.value, Assembly.GRCH38.value
    )
    assert enfusion_fusor_unknown.structure[0] == UnknownGeneElement()
    assert enfusion_fusor_unknown.viccNomenclature == "?::NM_002609.4(PDGFRB):e.11-559"
    enfusion.gene_5prime = "TPM3"
    enfusion.gene_3prime = "NA"
    enfusion_fusor_unknown = await translator.translate(
        enfusion, CoordinateType.RESIDUE.value, Assembly.GRCH38.value
    )
    assert enfusion_fusor_unknown.structure[1] == UnknownGeneElement()
    assert enfusion_fusor_unknown.viccNomenclature == "NM_152263.4(TPM3):e.4+5::?"


@pytest.mark.asyncio
async def test_genie(
    fusion_data_example, fusion_data_example_nonexonic, fusor_instance
):
    """Test GENIE Translator"""
    translator = GenieTranslator(fusor=fusor_instance)
    # Test exonic breakpoint
    genie = Genie(
        site1_hugo="TPM3",
        site2_hugo="PDGFRB",
        site1_chrom=1,
        site2_chrom=5,
        site1_pos=154170465,
        site2_pos=150126612,
        annot="TMP3 (NM_152263.4) - PDGFRB (NM_002609.4) fusion",
        reading_frame="In_frame",
    )

    genie_fusor = await translator.translate(
        genie,
        CoordinateType.INTER_RESIDUE.value,
        Assembly.GRCH38.value,
    )
    assert genie_fusor.structure == fusion_data_example().structure
    assert genie_fusor.viccNomenclature == fusion_data_example().viccNomenclature

    # Test non-exonic breakpoint
    genie.site1_pos = 154173079
    genie.site2_pos = 150127173

    genie_fusor_nonexonic = await translator.translate(
        genie,
        CoordinateType.RESIDUE.value,
        Assembly.GRCH38.value,
    )
    assert genie_fusor_nonexonic.structure == fusion_data_example_nonexonic().structure
    assert (
        genie_fusor_nonexonic.viccNomenclature
        == fusion_data_example_nonexonic().viccNomenclature
    )

    # Test unknown partner
    genie.site1_hugo = "NA"
    genie_fusor_unknown = await translator.translate(
        genie, CoordinateType.RESIDUE.value, Assembly.GRCH38.value
    )
    assert genie_fusor_unknown.structure[0] == UnknownGeneElement()
    assert genie_fusor_unknown.viccNomenclature == "?::NM_002609.4(PDGFRB):e.11-559"
    genie.site1_hugo = "TPM3"
    genie.site2_hugo = "NA"
    genie_fusor_unknown = await translator.translate(
        genie, CoordinateType.RESIDUE.value, Assembly.GRCH38.value
    )
    assert genie_fusor_unknown.structure[1] == UnknownGeneElement()
    assert genie_fusor_unknown.viccNomenclature == "NM_152263.4(TPM3):e.4+5::?"


@pytest.mark.asyncio
async def test_civic(
    fusion_data_example_categorical,
    fusion_data_example_categorical_mpge,
    fusion_data_example_categorical_nonzerooffset,
    fusor_instance,
    fixture_data_dir,
):
    """Test CIVIC translator"""
    translator = CIVICTranslator(fusor=fusor_instance)
    path = fixture_data_dir / "test_civic_cache.pkl"
    with Path.open(path, "rb") as cache_file:
        fusions_list = pickle.load(cache_file)  # noqa: S301

    # Test case where both gene partners known
    test_fusion = CIVIC(
        vicc_compliant_name=fusions_list[0].vicc_compliant_name,
        five_prime_end_exon_coords=fusions_list[0].five_prime_end_exon_coordinates,
        three_prime_start_exon_coords=fusions_list[
            0
        ].three_prime_start_exon_coordinates,
        molecular_profiles=fusions_list[0].molecular_profiles,
    )
    civic_fusor = await translator.translate(test_fusion)
    assert civic_fusor.structure == fusion_data_example_categorical().structure
    assert (
        civic_fusor.viccNomenclature
        == fusion_data_example_categorical().viccNomenclature
    )
    assert len(civic_fusor.civicMolecularProfiles) == 64

    # Test case where one partner is a MultiplePossibleGenesElement object
    test_fusion = CIVIC(
        vicc_compliant_name=fusions_list[1].vicc_compliant_name,
        five_prime_end_exon_coords=fusions_list[1].five_prime_end_exon_coordinates,
        three_prime_start_exon_coords=fusions_list[
            1
        ].three_prime_start_exon_coordinates,
        molecular_profiles=fusions_list[1].molecular_profiles,
    )
    civic_fusor = await translator.translate(test_fusion)
    assert civic_fusor.structure == fusion_data_example_categorical_mpge().structure
    assert (
        civic_fusor.viccNomenclature
        == fusion_data_example_categorical_mpge().viccNomenclature
    )
    assert len(civic_fusor.civicMolecularProfiles) == 1

    # Test case where there is a non-zero offset
    test_fusion = CIVIC(
        vicc_compliant_name=fusions_list[2].vicc_compliant_name,
        five_prime_end_exon_coords=fusions_list[2].five_prime_end_exon_coordinates,
        three_prime_start_exon_coords=fusions_list[
            2
        ].three_prime_start_exon_coordinates,
        molecular_profiles=fusions_list[2].molecular_profiles,
    )
    civic_fusor = await translator.translate(test_fusion)
    assert (
        civic_fusor.structure
        == fusion_data_example_categorical_nonzerooffset().structure
    )
    assert (
        civic_fusor.viccNomenclature
        == fusion_data_example_categorical_nonzerooffset().viccNomenclature
    )
    assert len(civic_fusor.civicMolecularProfiles) == 1


def test_moa(fusor_instance):
    """Test MOATranslator"""
    translator = MOATranslator(fusor=fusor_instance)

    # Test BCR::ABL1 example
    moa_assertion_example_bcr_abl = {
        "id": 109,
        "type": "Statement",
        "description": "The U.S. Food and Drug Administration granted approval to dasatinib for the treatment of newly diagnosed adult patients with Philadelphia chromosome-positive (Ph+) chronic myeloid leukemia (CML) in chronic phase.",
        "contributions": [
            {
                "id": 0,
                "type": "Contribution",
                "description": "Initial access of FDA approvals",
                "date": "2024-10-30",
                "agent": {
                    "id": 0,
                    "type": "Agent",
                    "subtype": "organization",
                    "name": "Van Allen lab",
                    "description": "Van Allen lab, Dana-Farber Cancer Institute",
                },
            }
        ],
        "reportedIn": [
            {
                "id": "doc:fda.sprycel",
                "type": "Document",
                "subtype": "Regulatory approval",
                "name": "Sprycel (dasatinib) [package insert]. FDA.",
                "citation": "Bristol-Myers Squibb Company. Sprycel (dasatinib) [package insert]. U.S. Food and Drug Administration website. https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/021986s027lbl.pdf. Revised February 2023. Accessed October 30, 2024.",
                "company": "Bristol-Myers Squibb Company.",
                "drug_name_brand": "Sprycel",
                "drug_name_generic": "dasatinib",
                "first_published": None,
                "access_date": "2024-10-30",
                "publication_date": "2023-02-08",
                "url": "https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/021986s027lbl.pdf",
                "url_drug": "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo=021986",
                "application_number": 21986,
                "organization": {
                    "id": "fda",
                    "name": "Food and Drug Administration",
                    "description": "Regulatory agency that approves drugs for use in the United States.",
                    "url": "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm",
                    "last_updated": "2025-06-12",
                },
            }
        ],
        "indication": {
            "id": "ind:fda.sprycel:0",
            "indication": "SPRYCEL is a kinase inhibitor indicated for the treatment of newly diagnosed adults with Philadelphia chromosome-positive (Ph+) chronic myeloid leukemia (CML) in chronic phase.",
            "initial_approval_date": "2015-08-12",
            "initial_approval_url": "https://www.accessdata.fda.gov/drugsatfda_docs/label/2015/021986s016s017lbledt.pdf",
            "description": "The U.S. Food and Drug Administration granted approval to dasatinib for the treatment of newly diagnosed adult patients with Philadelphia chromosome-positive (Ph+) chronic myeloid leukemia (CML) in chronic phase.",
            "raw_biomarkers": "philadelphia chromosome-positive (Ph+)",
            "raw_cancer_type": "philadelphia chromosome-positive (Ph+) chronic myeloid leukemia (CML)",
            "raw_therapeutics": "Sprycel (dasatinib)",
        },
        "proposition": {
            "id": 98,
            "type": "VariantTherapeuticResponseProposition",
            "predicate": "predictSensitivityTo",
            "biomarkers": [
                {
                    "id": 12,
                    "type": "CategoricalVariant",
                    "name": "BCR::ABL1",
                    "genes": [
                        {
                            "id": 6,
                            "conceptType": "Gene",
                            "name": "BCR",
                            "mappings": [
                                {
                                    "relation": "exactMatch",
                                    "coding": {
                                        "id": "ensembl:ensg00000186716",
                                        "code": "ENSG00000186716",
                                        "system": "https://www.ensembl.org",
                                    },
                                },
                                {
                                    "relation": "exactMatch",
                                    "coding": {
                                        "id": "ncbi:613",
                                        "code": "613",
                                        "system": "https://www.ncbi.nlm.nih.gov/gene",
                                    },
                                },
                                {
                                    "relation": "relatedMatch",
                                    "coding": {
                                        "id": "refseq:NM_004327.4",
                                        "code": "NM_004327.4",
                                        "system": "https://www.ncbi.nlm.nih.gov/nuccore",
                                    },
                                },
                            ],
                            "extensions": [
                                {"name": "location", "value": "22q11.23"},
                                {"name": "location_sortable", "value": "22q11.23"},
                            ],
                            "primaryCoding": {
                                "id": "hgnc:1014",
                                "code": "HGNC:1014",
                                "system": "https://genenames.org",
                            },
                        },
                        {
                            "id": 0,
                            "conceptType": "Gene",
                            "name": "ABL1",
                            "mappings": [
                                {
                                    "relation": "exactMatch",
                                    "coding": {
                                        "id": "ensembl:ensg00000097007",
                                        "code": "ENSG00000097007",
                                        "system": "https://www.ensembl.org",
                                    },
                                },
                                {
                                    "relation": "exactMatch",
                                    "coding": {
                                        "id": "ncbi:25",
                                        "code": "25",
                                        "system": "https://www.ncbi.nlm.nih.gov/gene",
                                    },
                                },
                                {
                                    "relation": "relatedMatch",
                                    "coding": {
                                        "id": "refseq:NM_005157.6",
                                        "code": "NM_005157.6",
                                        "system": "https://www.ncbi.nlm.nih.gov/nuccore",
                                    },
                                },
                            ],
                            "extensions": [
                                {"name": "location", "value": "9q34.12"},
                                {"name": "location_sortable", "value": "09q34.12"},
                            ],
                            "primaryCoding": {
                                "id": "hgnc:76",
                                "code": "HGNC:76",
                                "system": "https://genenames.org",
                            },
                        },
                    ],
                    "extensions": [
                        {"name": "biomarker_type", "value": "Rearrangement"},
                        {"name": "rearrangement_type", "value": "Fusion"},
                        {"name": "locus", "value": None},
                        {"name": "_present", "value": True},
                    ],
                }
            ],
            "subjectVariant": {},
            "conditionQualifier": {
                "id": 71,
                "conceptType": "Disease",
                "name": "Chronic Myeloid Leukemia, BCR-ABL1+",
                "extensions": [
                    {
                        "name": "solid_tumor",
                        "value": None,
                        "description": "Boolean value for if this tumor type is categorized as a solid tumor.",
                    }
                ],
                "primaryCoding": {
                    "id": "oncotree:CMLBCRABL1",
                    "code": "CMLBCRABL1",
                    "name": "Chronic Myeloid Leukemia, BCR-ABL1+",
                    "system": "https://oncotree.mskcc.org",
                },
            },
            "objectTherapeutic": {
                "id": 84,
                "conceptType": "Drug",
                "name": "Dasatinib",
                "extensions": [
                    {"name": "therapy_strategy", "value": ["BCR-ABL inhibition"]},
                    {"name": "therapy_type", "value": "Targeted therapy"},
                ],
                "primaryCoding": {
                    "id": "ncit:C38713",
                    "code": "C38713",
                    "name": "Dasatinib",
                    "system": "https://evsexplore.semantics.cancer.gov",
                },
            },
        },
        "strength": {
            "id": 0,
            "conceptType": "Evidence",
            "name": "Approval",
            "primaryCoding": {
                "id": "ncit:C25425",
                "code": "C25425",
                "name": "Approval",
                "system": "https://evsexplore.semantics.cancer.gov",
            },
        },
    }

    moa_fusion = translator.translate(moa_assertion_example_bcr_abl)
    assert moa_fusion.structure[0] == fusor_instance.gene_element("BCR")[0]
    assert moa_fusion.structure[1] == fusor_instance.gene_element("ABL1")[0]
    assert moa_fusion.moaAssertion == moa_assertion_example_bcr_abl

    # Test v::ALK example
    moa_assertion_example_v_alk = {
        "id": 23,
        "type": "Statement",
        "description": "The U.S. Food and Drug Administration granted approval to alectinib for the adjuvant treatment of adult patients, following tumor resection, with anaplastic lymphoma kinase (ALK)-positive non-small cell lung cancer (NSCLC) (tumors >= 4 cm or node positive), as detected by an FDA-approved test.",
        "contributions": [
            {
                "id": 0,
                "type": "Contribution",
                "description": "Initial access of FDA approvals",
                "date": "2024-10-30",
                "agent": {
                    "id": 0,
                    "type": "Agent",
                    "subtype": "organization",
                    "name": "Van Allen lab",
                    "description": "Van Allen lab, Dana-Farber Cancer Institute",
                },
            }
        ],
        "reportedIn": [
            {
                "id": "doc:fda.alecensa",
                "type": "Document",
                "subtype": "Regulatory approval",
                "name": "Alecensa (alectinib) [package insert]. FDA.",
                "citation": "Genentech, Inc. Alecensa (alectinib) [package insert]. U.S. Food and Drug Administration website. https://www.accessdata.fda.gov/drugsatfda_docs/label/2024/208434s015lbl.pdf. Revised February 2023. Accessed October 30, 2024.",
                "company": "Genentech, Inc.",
                "drug_name_brand": "Alecensa",
                "drug_name_generic": "alectinib",
                "access_date": "2024-10-30",
                "publication_date": "2024-04-18",
                "url": "https://www.accessdata.fda.gov/drugsatfda_docs/label/2024/208434s015lbl.pdf",
                "url_drug": "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo=208434",
                "application_number": 208434,
                "organization": {
                    "id": "fda",
                    "name": "Food and Drug Administration",
                    "description": "Regulatory agency that approves drugs for use in the United States.",
                    "url": "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm",
                    "last_updated": "2025-06-12",
                },
            }
        ],
        "direction": "supports",
        "indication": {
            "id": "ind:fda.alecensa:0",
            "indication": "ALECENSA is a kinase inhibitor indicated for the adjuvant treatment in adult patients following tumor resection of anaplastic lymphoma kinase (ALK)-positive non-small cell lung cancer (NSCLC) (tumors >= 4 cm or node positive) as detected by an FDA-approved test.",
            "initial_approval_date": "2024-04-18",
            "initial_approval_url": "https://www.accessdata.fda.gov/drugsatfda_docs/label/2024/208434s015lbl.pdf",
            "description": "The U.S. Food and Drug Administration granted approval to alectinib for the adjuvant treatment of adult patients, following tumor resection, with anaplastic lymphoma kinase (ALK)-positive non-small cell lung cancer (NSCLC) (tumors >= 4 cm or node positive), as detected by an FDA-approved test.",
            "raw_biomarkers": "ALK-positive",
            "raw_cancer_type": "non-small cell lung cancer",
            "raw_therapeutics": "Alecensa (alectinib)",
        },
        "proposition": {
            "id": 22,
            "type": "VariantTherapeuticResponseProposition",
            "predicate": "predictSensitivityTo",
            "biomarkers": [
                {
                    "id": 8,
                    "type": "CategoricalVariant",
                    "name": "v::ALK",
                    "genes": [
                        {
                            "id": 2,
                            "conceptType": "Gene",
                            "name": "ALK",
                            "mappings": [
                                {
                                    "relation": "exactMatch",
                                    "coding": {
                                        "id": "ensembl:ensg00000171094",
                                        "code": "ENSG00000171094",
                                        "system": "https://www.ensembl.org",
                                    },
                                },
                                {
                                    "relation": "exactMatch",
                                    "coding": {
                                        "id": "ncbi:238",
                                        "code": "238",
                                        "system": "https://www.ncbi.nlm.nih.gov/gene",
                                    },
                                },
                                {
                                    "relation": "relatedMatch",
                                    "coding": {
                                        "id": "refseq:NM_004304.5",
                                        "code": "NM_004304.5",
                                        "system": "https://www.ncbi.nlm.nih.gov/nuccore",
                                    },
                                },
                            ],
                            "extensions": [
                                {"name": "location", "value": "2p23.2-p23.1"},
                                {"name": "location_sortable", "value": "02p23.2-p23.1"},
                            ],
                            "primaryCoding": {
                                "id": "hgnc:427",
                                "code": "HGNC:427",
                                "system": "https://genenames.org",
                            },
                        }
                    ],
                    "extensions": [
                        {"name": "biomarker_type", "value": "Rearrangement"},
                        {"name": "rearrangement_type", "value": "Fusion"},
                        {"name": "locus", "value": None},
                        {"name": "_present", "value": True},
                    ],
                }
            ],
            "subjectVariant": {},
            "conditionQualifier": {
                "id": 47,
                "conceptType": "Disease",
                "name": "Non-Small Cell Lung Cancer",
                "extensions": [
                    {
                        "name": "solid_tumor",
                        "value": True,
                        "description": "Boolean value for if this tumor type is categorized as a solid tumor.",
                    }
                ],
                "primaryCoding": {
                    "id": "oncotree:NSCLC",
                    "code": "NSCLC",
                    "name": "Non-Small Cell Lung Cancer",
                    "system": "https://oncotree.mskcc.org",
                },
            },
            "objectTherapeutic": {
                "id": 9,
                "conceptType": "Drug",
                "name": "Alectinib",
                "extensions": [
                    {"name": "therapy_strategy", "value": ["ALK inhibition"]},
                    {"name": "therapy_type", "value": "Targeted therapy"},
                ],
                "primaryCoding": {
                    "id": "ncit:C101790",
                    "code": "C101790",
                    "name": "Alectinib",
                    "system": "https://evsexplore.semantics.cancer.gov",
                },
            },
        },
        "strength": {
            "id": 0,
            "conceptType": "Evidence",
            "name": "Approval",
            "primaryCoding": {
                "id": "ncit:C25425",
                "code": "C25425",
                "name": "Approval",
                "system": "https://evsexplore.semantics.cancer.gov",
            },
        },
    }

    moa_fusion = translator.translate(moa_assertion_example_v_alk)
    assert moa_fusion.structure[0] == fusor_instance.multiple_possible_genes_element()
    assert moa_fusion.structure[1] == fusor_instance.gene_element("ALK")[0]
    assert moa_fusion.moaAssertion == moa_assertion_example_v_alk
