## R-RN-Classification
Workspace for developing the R-RN global checklist

## OVERVIEW

To support the work of the Rhododendron research and conservation communities, we will update the Rhododendron checklist in the World Flora Online (WFO). 
We will curate the taxonomic backbone in the WFO by expanding it to include updated nomenclatural information from a variety of existing data sources. 
We will disambiguate common orthographic variants within the database and present an overview of these.
Our goal is to create the most robust database of Rhododendron names and thereby provide a reliable reference for initiatives in research and conservation. 
We will recruit participants and distribute information about this project and products arising from this work via the Rhododendron Research Network.

## INTENDED PRODUCTS

We will create a comprehensive and maintained checklist of *_Rhododendron_*.
We will continually mataintain and improve the data in the *World Flora Online* for each of thier 6-monthly releases https://www.worldfloraonline.org/.
We will archive checklist in the Rhododendron Research Network Zenodo archive https://zenodo.org/communities/rhododendron/records.
We will enhance our existing Zotero literature database https://www.zotero.org/groups/4735534/rhodo-research.net. 
We will create a webpage within the Rhododendron Research Network Website with links to all of these resources. 
We will publish a paper in an academic journal to disseminate this work.

## PROCESS

We will correct nomenclatural records in Rhakhis.
We will produce spreadsheets to facilitate acces for others.

There will be a Python scripts created by Alan Elliott that will access the staged data in the WFO via a GraphQL API to generate a CSV files, in the Darwin Core Format, which contain taxon names and data associated with that taxon. These scripts will be available online for download by contributors, who can use the scripts to obtain species for editing, if they do not want to edit directly in Rhakhis. 

Our current idea is that R-RN participants will adopt taxa with which they have expertise, and they will vet the species lists for those taxa. 
Following, they will re-upload proposed changes back to the master list, where we’ll apply some sort of voting (to be determined) to ensure a baseline degree of quality and consistency.

We will invite participants from the larger Rhododendron community, including academic scientists, botanical garden staff and expert volunteers (e.g., American Rhododendron Society). We will use email contact lists of the R-RN to identify and invite potential participants.

## VOTING

We will create a form here that will raise a GitHub an issue. There will be a period of time where the issues proposals can be discusses. A google form will be shared via an email list to voting can take place. With 2/3rd majority of those who vote. This needs discussed and decided.

## VERSIONING
We expect this project to produce updates to the taxonomic database. The working group leader (Alan Elliott) will be in charge of issuing updates to WFO. The R-RN community will be notified before any major updates. Only changes that have been approved by the voting system will be included in updates. A DOI will be provided for each version via Zenodo. 
how are versions managed by the Rhakhis system? How exactly are updates passed to WFO? 

## Reference Library
A Zotero library is being maintained by Juliana Medeiros to store references relevant to R-RN. Data sources will include items currently contained in the R-RN Zotero database. Additional resources identified by the group will be added to the Zotero database. We will especially strive to add smaller, regional publications, including making translations into English using Google translate, combined with vetting of translations by native language speakers.

If you want to suggest literature please check if it is in (Zotero)[https://www.zotero.org/groups/4735534/rhodo-research.net/library], if not please suggest it (here.)[https://github.com/RhodoResearchNetwork/RRN-Classification/issues/new/choose]



## Contributing

All taxonomic decisions are made by the R-RN community.

Taxonomic proposals should be submitted as issues, which will be voted on monthly. Proposals may be commented upon in the issue tracker. Voting is carried out separately via a Google Form survey circulated on the PPG mailing list. Any proposal receiving >2/3 support will be approved and implemented in the data.


## Code of Conduct

All participants agree to adhere to the [code of conduct](docs/Code%20of%20Conduct.md).

## Why GitHub?

GitHub provides tools to allow us to have open, collaborative discussions of taxonomic proposals, and to maintain a record of those discussions publicly available in perpetuity.

## Why Rhakhis?

The use of Rhaksis allow us to maintain names at the species level in an effective manner, and credit those involved via the WFO data releases. The 6-month releases by the WFO gives us discrete deadlines in the year to aim for.
