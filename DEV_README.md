# Developer notes

## Selectors on fda.gov letter pages

Pick boxes by HTML tag or role, not by class name.

- `dt` and `dt + dd` read the label-value pairs, such as Product and Issuing Office.
- `div[role=main]` holds the letter text.

Why: fda.gov splits the fields across 3 `<dl>` boxes. Only one has a class
(`lcds-description-list--grid`), and it holds 3 of the 5 fields.
Class names are design names, and a restyle silently drops fields.

Use a class only when no tag or role marks the box you need.
