"""Script for creating JSON examples in src/fusor/examples"""

import asyncio
import json
from pathlib import Path

import anyio
from pydantic import BaseModel

from fusor import FUSOR
from fusor.models import (
    Assay,
    CausativeEvent,
    DomainStatus,
    EventType,
    Evidence,
    RegulatoryClass,
)

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "src" / "fusor" / "examples"


async def _create_json(fn: str, model: BaseModel) -> None:
    """Create JSON file in examples directory

    :param fn: File name
    :param model: Fusion model
    """
    async with await anyio.open_file(EXAMPLES_DIR / fn, "w") as wf:
        await wf.write(json.dumps(model.model_dump(exclude_none=True), indent=2))


async def create_alk(f: FUSOR) -> None:
    """Create JSON file for minimal ALK categorical fusion

    :param f: FUSOR instance
    """
    multiple_possible_genes = f.multiple_possible_genes_element()
    gene, _ = f.gene_element("ALK", use_minimal_gene=True)
    functional_domain, _ = f.functional_domain(
        status=DomainStatus.PRESERVED,
        name="Protein kinase, ATP binding site",
        functional_domain_id="interpro:IPR017441",
        gene="ALK",
        sequence_id="NP_004295.2",
        start=1122,
        end=1150,
        use_minimal_gene=True,
    )

    categorical_fusion = f.categorical_fusion(
        structure=[multiple_possible_genes, gene],
        critical_functional_domains=[functional_domain],
    )
    await _create_json("alk.json", categorical_fusion)


async def create_bcr_abl1(f: FUSOR) -> None:
    """Create JSON files for minimal and expanded BCR ABL1 categorical fusion

    :param f: FUSOR instance
    """
    for use_minimal_gene in [True, False]:
        tse1, _ = await f.transcript_segment_element(
            tx_to_genomic_coords=True,
            use_minimal_gene=use_minimal_gene,
            gene="BCR",
            transcript="NM_004327.3",
            exon_end=2,
            exon_end_offset=182,
        )

        linker_element, _ = f.linker_element("ACTAAAGCG")

        tse2, _ = await f.transcript_segment_element(
            tx_to_genomic_coords=True,
            use_minimal_gene=use_minimal_gene,
            gene="ABL1",
            transcript="NM_005157.5",
            exon_start=2,
            exon_start_offset=-173,
        )

        functional_domain, _ = f.functional_domain(
            status=DomainStatus.PRESERVED,
            name="SH2 domain",
            functional_domain_id="interpro:IPR000980",
            gene="ABL1",
            sequence_id="NP_005148.2",
            start=127,
            end=202,
            use_minimal_gene=use_minimal_gene,
        )

        categorical_fusion = f.categorical_fusion(
            structure=[tse1, linker_element, tse2],
            critical_functional_domains=[functional_domain],
            reading_frame_preserved=True,
        )

        fn = "bcr_abl1.json" if use_minimal_gene else "bcr_abl1_expanded.json"
        await _create_json(fn, categorical_fusion)


async def create_ewsr1(f: FUSOR) -> None:
    """Create JSON files for EWSR1 assayed fusion

    :param f: FUSOR instance
    """
    gene, _ = f.gene_element("EWSR1", use_minimal_gene=True)
    unknown_gene = f.unknown_gene_element()
    assayed_fusion = f.assayed_fusion(structure=[gene, unknown_gene])
    await _create_json("ewsr1_elements_only.json", assayed_fusion)

    causative_event = CausativeEvent(eventType=EventType.REARRANGEMENT)
    assayed_fusion = f.assayed_fusion(
        structure=[gene, unknown_gene], causative_event=causative_event
    )
    await _create_json("ewsr1_no_assay.json", assayed_fusion)

    assay = Assay(
        assayName="fluorescence in-situ hybridization assay",
        assayId="obi:OBI_0003094",
        methodUri="pmid:33576979",
        fusionDetection=Evidence.INFERRED,
    )
    assayed_fusion = f.assayed_fusion(
        structure=[gene, unknown_gene], causative_event=causative_event, assay=assay
    )
    await _create_json("ewsr1.json", assayed_fusion)

    assayed_fusion = f.assayed_fusion(structure=[gene, unknown_gene], assay=assay)
    await _create_json("ewsr1_no_causative_event.json", assayed_fusion)


async def create_igh_myc(f: FUSOR) -> None:
    """Create JSON files for IGH MYC categorical fusion

    :param f: FUSOR instance
    """
    reg_el, _ = f.regulatory_element(
        RegulatoryClass.ENHANCER, "IGH", use_minimal_gene=True
    )
    reg_el.featureId = "EH38E3121735"
    gene, _ = f.gene_element("MYC", use_minimal_gene=True)
    categorical_fusion = f.categorical_fusion(
        regulatory_element=reg_el,
        structure=[gene],
    )
    await _create_json("igh_myc.json", categorical_fusion)


async def create_tpm3_ntrk1(f: FUSOR) -> None:
    """Create JSON files for minimal and expanded TPM3 NTRK1 assayed fusion

    :param f: FUSOR instance
    """
    tse1, _ = await f.transcript_segment_element(
        tx_to_genomic_coords=True,
        use_minimal_gene=True,
        gene="TPM3",
        transcript="NM_152263.3",
        exon_end=8,
        exon_end_offset=0,
    )
    tse2, _ = await f.transcript_segment_element(
        tx_to_genomic_coords=True,
        use_minimal_gene=True,
        gene="NTRK1",
        transcript="NM_002529.3",
        exon_start=10,
        exon_start_offset=-0,
    )
    causative_event = CausativeEvent(eventType=EventType.REARRANGEMENT)
    assay = Assay(
        assayName="fluorescence in-situ hybridization assay",
        assayId="obi:OBI_0003094",
        methodUri="pmid:33576979",
        fusionDetection=Evidence.INFERRED,
    )
    assayed_fusion = f.assayed_fusion(
        structure=[tse1, tse2], causative_event=causative_event, assay=assay
    )
    await _create_json("tpm3_ntrk1.json", assayed_fusion)


async def create_tpm3_pdgfrb(f: FUSOR) -> None:
    """Create JSON files for minimal and expanded TPM3 PDGFRB assayed fusion

    :param f: FUSOR instance
    """
    tse1, _ = await f.transcript_segment_element(
        tx_to_genomic_coords=True,
        use_minimal_gene=True,
        gene="TPM3",
        transcript="NM_152263.3",
        exon_start=1,
        exon_start_offset=0,
        exon_end=8,
        exon_end_offset=0,
    )
    tse2, _ = await f.transcript_segment_element(
        tx_to_genomic_coords=True,
        use_minimal_gene=True,
        gene="PDGFRB",
        transcript="NM_002609.3",
        exon_start=11,
        exon_start_offset=-0,
        exon_end=22,
        exon_end_offset=0,
    )
    causative_event = CausativeEvent(eventType=EventType.REARRANGEMENT)
    assay = Assay(
        assayName="RT-PCR",
        assayId="obi:OBI_0000552",
        methodUri="pmid:24034314",
        fusionDetection=Evidence.OBSERVED,
    )
    assayed_fusion = f.assayed_fusion(
        structure=[tse1, tse2], causative_event=causative_event, assay=assay
    )
    await _create_json("tpm3_pdgfrb.json", assayed_fusion)


async def create_all_examples() -> None:
    """Create all Categorical and Assay Fusion examples"""
    f = FUSOR()
    await create_alk(f)
    await create_bcr_abl1(f)
    await create_ewsr1(f)
    await create_igh_myc(f)
    await create_tpm3_ntrk1(f)
    await create_tpm3_pdgfrb(f)


if __name__ == "__main__":
    asyncio.run(create_all_examples())
