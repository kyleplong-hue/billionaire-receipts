# Latest receipt standard (current)

The three `<article class="receipt">` posts in `index.html` are the reference. New receipts belong inside `<main>`, above `#archive` (newest first), not as short Archive entries. Start with `templates/feature-post.html`. The site uses a centered, single-column reading flow on desktop and mobile; do not restore two-column cards or screenshot galleries.

## Required before publishing

1. **Said:** name/topic, exact dated quote, clear venue/attribution, and one genuinely sourced evidence image that links to the depicted original source or court record. Explain the image's provenance accurately; a later court reproduction of an older quote is not a screenshot of the original article. If no genuine visual is available, omit the figure rather than inventing one.
2. **Then:** dated, precisely sourced outcome; one concise red editorial line; a short context paragraph for caveats, timing, appeal status, or the distinction between a person's statement and a company's liability.
3. **Actions:** link to a genuinely relevant publisher video when available (a `.watch` link, never an embedded iframe); include every useful original/outcome/reporting link in a single `<details class="sources">` list, oldest first, with an accurate `Sources (n)` count. Don't include empty video placeholders.
4. Preserve exact source URLs. Distinguish exact quotations from paraphrases and a change in conduct/advice from a change in belief. Verify dates, amounts, attribution, and names against primary records and reporting. Do not present editorial inference as a court finding.
5. Use the existing CSS and colors. One image per receipt is the visual limit; additional contemporaneous and later headlines belong as links in Sources. Keep image alt text and caption honest.

Before pushing: check the quote and outcome against their linked sources; verify images and links; test desktop (1440px), tablet (768px), and mobile (390px) for no horizontal scroll; open/close Sources and check counts; test Archive filters/search; confirm no console errors. After pushing, verify GitHub Pages built and the live site, images, and deep links work. The Archive remains separate and unchanged.
