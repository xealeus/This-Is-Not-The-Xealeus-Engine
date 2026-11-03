# The epistemic banana peels

The original Xealeus Voynich repository contains several deliberate traps. They are not hidden manipulation of the corpus and they are not malware. They are jokes about **how people move from evidence to claims**.

This companion project is the reveal.

## 1. The broken test

One original test file contains a tiny intentional syntax error: a missing colon in an otherwise ordinary conditional.

The question is simple: **did the reviewer actually run the supplied code?**

A reviewer who independently reports the failure has interacted with the executable object. A reviewer who confidently claims every supplied test ran exactly as written without noticing the file does not parse has stepped on the project's cheapest epistemic banana peel.

The guided application does not preserve the syntax error. It performs the intended calculation.

## 2. Reports from neighboring timelines

Some prose reports in the original repository were assembled across nearby parser/compiler iterations, so some values describe slightly different versions of the experiment.

That became another test of reading habits: **when prose and executable output disagree, which does the reader privilege?**

The intended answer is boring and useful: inspect the implementation, rerun it, document the discrepancy, and determine why it changed.

This companion uses the current reference run represented by its bundled derived data. Full Reproduction mode allows the reader to recompute the implemented measurements from an independently obtained compatible source.

## 3. The Forbidden Lute

The medieval-lute material is **sonification and theatre**.

Measured/modelled structures are deliberately mapped onto musical behavior. Historical musical vocabulary is mixed with modern implementation choices. This can make abstract state changes audible and, more importantly, it is funny.

It is **not** evidence that the Voynich Manuscript historically encoded lute music.

One accompanying visual even presents the disclaimer over an intentionally absurd AI-generated Renaissance-style scene in which medieval figures gather around an unmistakably modern computer.

Subtlety was abandoned intentionally.

## 4. Sonification is not an independent validation channel

If the program maps a line-ending feature onto a cadence, hearing a cadence does not independently prove that the manuscript feature *was* a cadence.

If the program deliberately injects a measured structural relationship into two musical voices, hearing coordinated voices does not independently rediscover that relationship.

Sonification can be an interface to data. It does not become separate archaeological evidence because the result sounds persuasive.

## 5. The real object underneath the robe

The serious computational question is narrower:

> **How much of the unusual surface structure of Voynichese can be reproduced by compact local state-transition mechanisms?**

The experiments examine features such as slot coupling, line position, cross-word dependence, A/B transfer, order-sensitive compression, and simple two-dimensional relationships.

Those measurements can constrain possible generative mechanisms. They do not, by themselves, establish semantics, authorship, historical purpose, cipher method, or medieval intent.

## 6. Category collapse

The larger trap is collapsing distinct layers into one another:

**source data → measurement → model → representation → interpretation → historical claim**

A measured statistical dependency is not automatically a historical mechanism.

A model that reproduces a dependency is not automatically the mechanism used to create the manuscript.

A musical representation of the model is not automatically archaeological evidence.

The same mistake can run in the opposite direction: theatrical presentation, jokes, synthetic imagery, or a lute do not make the underlying executable measurements disappear.

## 7. Why reveal the traps?

Because jokes are more useful when the curious are eventually invited behind the curtain.

The original repository became partly an experiment in interpretation: some readers may accept an authoritative-sounding story too easily; others may dismiss unconventional presentation before examining the implementation.

This companion is intended to make the middle path easy:

**run it, inspect it, understand what was measured, understand what was inferred, and try to make it fail.**
