# Featured post standard (current)

The Musk post in `index.html` is the reference. Every new full post belongs in the `<main>` feed as an `<article class="feature secondary-feature">` immediately before `#archive`. The Trump post uses the same structure. Do **not** add a new story as a short `.entry` archive card in place of a full post.

Use `templates/feature-post.html` as the starting markup, with the shared `.feature` CSS already in `index.html`. Keep the page white, minimal, and two-column on desktop / stacked on mobile.

## Required before publishing

- **Left:** name and category; red date/context kicker above an *exact, dated* original quotation. Check wording and date against its linked primary/original reporting. Add a linked visual of the source (interview still if genuinely from that interview, or a clearly labeled screenshot of the article/quote); do not claim an illustrative still captures the exact spoken instant. Below it, include linked screenshots of reporting from the original period with accurate captions and alt text.
- **Right:** red “What happened · [date]” kicker; a precisely sourced later outcome or quotation, linked screenshot of an actual current article headline, short editorial passage that does not overclaim motive or erase caveats, and a centered relevant video embed with an external link to the video. Add direct source links for both the old claim and new outcome.
- Capture actual source pages, never fabricate or re-typeset headlines as screenshots. Store optimized image assets under `assets/`; make each capture link to the page it depicts. If a source is not accessible for a genuine capture, choose a different credible source rather than depicting a fake page.
- Keep quotes distinct from paraphrases, and distinguish a change in conduct/advice from a retraction of a belief. Verify the video publisher and that it is genuinely about this story. Do not publish an empty or unrelated video placeholder.
- Before pushing, verify the original and outcome text in the linked articles, check desktop/mobile layout (including no horizontal overflow), all images/links, and the live GitHub Pages build after pushing.

Archive cards are a separate legacy section; this standard governs every **new featured post**. Revisit the format only if Kyle explicitly changes it.
