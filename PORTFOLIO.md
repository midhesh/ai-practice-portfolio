# AI Practice Portfolio
### Midhesh Mahadevan Shankar

Most of the friction in adopting AI at work isn't really about the AI. It's about trust. People stop trusting a workflow the moment it quietly gets something wrong and nobody catches it, and once that trust is gone, the tool gets quietly abandoned even if it was mostly working. The four tools here each take on a small, specific version of that problem: information that gets lost between people, a process that looks reliable until it isn't, a trial that never gets judged against anything concrete, and a decision made in conversation that never makes it anywhere searchable. None of them are large systems. Each one is small enough to understand in a few minutes, and each one actually runs, with real results captured from real runs rather than described in the abstract.

Full code: github.com/midhesh/ai-decision-prompt-pilot-toolkit

![Four tools, one toolkit](./diagrams/portfolio_pipeline.png)

## 1. Decision Log

Say a decision gets made in a meeting or a quick back and forth on chat, and it never gets written down anywhere anyone would think to search. Weeks later someone else, working on something adjacent, makes the opposite call, with no way of knowing the first decision ever happened. Nobody notices until the two approaches run into each other.

This tool keeps a log of decisions along with the reasoning behind them, and it checks its own work. It runs in two passes: a fast check flags anything already on record that looks related to what's being logged, then a slower pass decides whether the two are actually connected or just happen to use similar words. A quick search alone can't tell those apart. It found this out the hard way in testing: two unrelated budget requests, one for sales travel and one for marketing sponsorships, shared close to seventy percent of their wording because both talked about increasing an annual budget to cover more industry events. A search that stopped at word overlap would have flagged them as related. The second pass correctly worked out that they weren't. In the same test run, a real duplicate decision, worded completely differently from the original, was caught and explained in a single sentence.

## 2. PromptGrade

An AI-assisted process gets tried a handful of times, looks fine, and quietly becomes part of how things get done. The one situation it consistently handles badly doesn't show up until it's already been leaned on for real work, usually because nobody's checking every single output once the tool starts feeling routine.

This tool uses the same two-pass idea as the decision log above, applied to a different question. It runs a process against a set of realistic situations, including the awkward edge cases people don't usually think to test for, and grades each response with a fast check first, then a slower pass that actually reads what the response means. When it finds a failure, it doesn't just report it. It works out what the response was missing and writes a specific fix, then checks that fix immediately rather than assuming it worked. This paid off twice during testing. Once, a version that looked solid, four correct answers out of five, turned out to be quietly getting one pattern wrong every time: it kept mistaking a recurring problem for a one-off. The fix generalized, confirmed on a completely new situation it hadn't seen before. The second time, the fast check caught its own limits. A response had been marked wrong purely because it avoided the exact wording expected, even though it was actually correct, and the slower pass recognized that.

## 3. AI Pilot Scorecard

A team runs an AI-assisted trial for a few weeks. It seems to help, more or less. Nobody agreed on a number that would count as success beforehand, so a few months later there's no way to say whether it actually worked. It just fades out, or limps along indefinitely without anyone deciding to properly commit to it. This happens often enough that a widely cited industry study found most AI pilots never make it to real, sustained use, for exactly this reason.

This tool makes a team write down, before the trial starts, one specific number that would count as success. Afterward, the real result gets checked against that number instead of a general impression. It also does something most scorecards skip. Even when the number looks good, it won't recommend expanding a pilot that involves sensitive information, an action that's hard to undo, or a process nobody is actually reviewing. Those get flagged as needing a fix first, with a specific explanation of what that fix should be. Tested with a one-line description, "drafts replies to client emails and sends them automatically without anyone reviewing first," it correctly pulled out three separate risk flags in a single pass. Separately, a pilot that beat its target by ten points was still correctly held back from a scale-up recommendation once flagged for touching an action that couldn't be undone with nobody checking the output. A scorecard that only looked at the number would have waved it through.

## 4. Meeting Bridge

Decisions get made inside meetings, not inside the decision log above, and nobody stops mid-conversation to fill out a form for it. Whatever got decided just sits inside raw meeting notes, next to reminders and small talk, and never becomes something anyone could search later.

This tool reads through raw meeting notes, picks out the paragraphs that sound like they contain an actual decision, and turns each one into a properly structured entry before logging it through the real decision log tool above, not a copy of it, the same code. Tested against eight paragraphs of ordinary, noisy meeting notes, it correctly picked out exactly two as decisions and left the rest alone: a broken coffee machine, an expense deadline, a passing compliment about some renders. One of the two extracted decisions was automatically recognized as very likely the same decision already made in an earlier, unrelated meeting, caught straight from raw notes with no manual tagging at all.

## Why build these four together

Each one is really the same lesson from a different angle: a fast, cheap signal, whether that's overlapping words, a keyword match, or a number that hit its target, gets mistaken for an actual judgment. The fix is the same every time, two passes, not one. Let the fast check do what it's good at, which is speed and coverage, and put the real thinking in a slower pass where the decision actually gets made. That's less about making AI smarter and more about making the process around it something people can actually rely on.
