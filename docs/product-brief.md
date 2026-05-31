# Holoform — Product Brief

> **Status:** Early concept. The product is being reimagined from its origin (an
> AI email-classification demo, still present in this repo and under `src/`) into
> a **neutral-fiduciary, multi-channel communication network**. This document is
> the canonical capture of that vision. It will move faster than the code.

_Working name: Holoform. A general-purpose messaging network that makes people
clearer to each other without ever making one person a target for another._

---

## The one-breath version

You bring a coach loyal to you. The other person's model is loyal to them, locked
in a neutral middle you can't interrogate. A broker passes between you only what
helps both — never what one could use against the other. It spans your channels
(email, Slack, and more) and a connection graph that lets trust travel between
people. And when things turn serious, the machine steps back and a human steps in.

---

## The three pillars

1. **Multi-channel.** Holoform is not an email app. It sits across the channels
   people actually use — email, Slack, and beyond — as one layer with many
   adapters. The original email classifier is the first channel adapter, not the
   product.
2. **Identity & trust graph.** A server-level graph of connections (think
   LinkedIn/Facebook in topology, not in purpose). The graph itself asserts trust
   between parties: a deeper, higher-frequency _bilateral_ connection between two
   people raises priority between them, and trust propagates across edges — if you
   have a strong connection to me, that edge carries some trust the first time you
   contact my wife.
3. **The fiduciary AI layer.** The neutral middle that models each person, stays
   loyal to the person it's describing, and passes to the other side only what
   helps both. Detailed below — it is the heart of the product.

The hard part is making these three obey **one** doctrine rather than three. See
[Open architectural questions](#open-architectural-questions).

---

## Pillar 3 — The fiduciary layer (the core)

### The one-sentence version

A messaging network with a neutral middle layer that holds a model of each person,
stays loyal to the person it's describing, and passes to the other side only what
helps both of them — never what one could use against the other. When a situation
turns serious, the machine steps back and a human steps in.

### How we got here

We started with an attractive but dangerous idea: a network that models _both
sides_ of every message. Each step of refining it revealed the same trap, and the
final design is the one that escapes it.

- **Model the recipient** (the Crystal Knows approach) → covert profiling. You're
  handed a manual for handling someone who never agreed to it.
- **Model both sides, mutually** → the most efficient manipulation engine ever
  built. Two profiles, each weaponizable.
- **Let agents negotiate for both sides** → the humans leave their own
  conversation, and you can no longer check whether you were represented honestly.
  The dishonesty just moves somewhere you can't see it.
- **A neutral counselor that comments instead of acting** → much safer, but its
  hidden power becomes _what it chooses to surface_, and the more gently it handles
  you, the more it has to know about you.
- **Each person writes their own "user manual"** → safe, because authorship is
  consent — but most people will never do the work.
- **Make the manual automatic** → removes the work, but quietly turns "B granted
  this" back into "the system inferred B," which is the original poison.

The resolution came from a single question: _how does a family therapist do this
safely?_ A therapist holds a model of everyone and translates between them — the
exact move we kept forbidding. Pulling apart _why_ it's safe gave us the final
architecture.

### The core insight

What makes a therapist safe is **not** that everyone's in the room (they often see
people one-on-one). It's **not** just confidentiality. The irreducible thing is:

> **The model is held by someone whose loyalty is to the person being modeled —
> never to the person they're currently helping.**

When a therapist sits alone with the husband and says "your wife isn't withholding
to punish you — she shuts down when she feels blamed," that's safe because the
therapist is _still the wife's fiduciary in that moment._ They will not say one
thing that harms her to help him win, even though he's the one in the chair.

A tool that _you_ own, running on _your_ phone, in _your_ interest, can never be
the other person's fiduciary. So the model of the other person cannot live in your
tool. It has to live in a neutral layer that answers to neither of you.

**That loyalty structure is the entire product. Everything else is plumbing for
it.**

### How it's built

Three separate pieces. The separation _is_ the safety.

**1. Your model — yours.** Built from how you actually communicate. It coaches you:
helps you avoid the angry version, helps you sound like your calm self. You're the
only one it serves. The other person never sees it.

**2. The other person's model — held by the neutral layer, loyal to them.** Built
from how they communicate. Critically: it does **not** live in your app, it does
**not** answer to you, and you **cannot** open it, query it, or ask it for their
"profile." It's locked — the way you can't phone your spouse's therapist and ask
for their file.

**3. The broker — decides what, if anything, crosses to you.** When you're writing
to someone, the broker consults their model and applies one test before surfacing
anything.

### The loyalty test (the one question, every time)

Before the layer tells you anything about the other person, it asks:

> **Does telling A this serve B and their relationship — or does it serve A against
> B?**

- Serves B and the relationship → **allowed.**
- Serves A against B → **blocked. Even if it's true. Even though A asked.**

**Same fact, two directions.** The underlying fact: _Maya gets anxious about
money._

- ✅ **Crosses to you:** "Money is a stressful topic for her — giving her the full
  picture up front lands better than dripping it out." _(Helps her feel safe and
  helps you. Allowed.)_
- ❌ **Never crosses to you:** "She's anxious about money, so stay vague and let her
  stew — she'll cave faster." _(Same fact, now a weapon. Blocked, permanently, even
  though it's true.)_

You never receive her psyche. You receive the operating instructions that make
things go better for both of you. You never receive the leverage.

### What "both ends" actually buys you

Most of the value does **not** come from her model reaching you. It comes from two
quieter things:

1. **Parallel self-regulation.** Her end is coaching _her_ to be calmer; your end is
   coaching _you_. You each receive a calmer version of the other. Nothing crosses
   between you — you just both have a good coach.
2. **Consented operating instructions.** A small, locked set of "how to reach me
   well" guidance, surfaced only when it passes the loyalty test.

If you ever find the other person's model affecting you in a way that helps you
_against_ them, the product is broken.

### General-purpose: one you, many relationships

This runs across your whole life — ex, best friend, kid's teacher, neighbor. The
power isn't a separate coach per person. It's that **you are the one constant
across all of it**, and the network is the only place that sees the whole graph.

- **One model of you, many registers.** Same you — brief-and-clear for the teacher,
  calm-and-unambiguous for your ex, unfiltered for your friend.
- **Protecting the walls between contexts.** The same fact belongs differently in
  each relationship (the Paris trip you joke about with a friend, mention
  logistically to your ex, don't mention to the neighbor). The system's job is to
  keep those walls intact and never let one context's framing or knowledge leak
  into another.

**Hard rule:** the network may model _you_ across all your contexts. It may
**never** assemble a model of anyone else across contexts — even from your own
data. Everyone else exists only as locked, fiduciary-held material inside the
relationships they're actually in.

### The bright line: where the machine stops and a human takes over

The layer handles the everyday well — phrasing, timing, sensitive topics, spotting
when you two are stuck in the same loop. That's ~95%.

But there's a ~5% where the right move is to **break the normal rules in someone's
interest**, and that always needs a human, because someone has to be accountable
for the call. The system hands off when:

- **Someone might get hurt.** If messages suggest danger — to either person or a
  child — "stay neutral, keep it private" no longer applies. The system stops
  smoothing, routes to a real person and real resources, and does not make that
  judgment alone.
- **The kind move is to confront, not soothe.** Telling someone they're deceiving
  themselves is a human call, not a machine's.
- **Interests genuinely collide and someone truly loses.** Not "A loses an unfair
  advantage" (that's just blocked) — a real conflict of welfare. The layer surfaces
  that there's a hard call and gets a person.

**The line, simply: the layer can carry what helps; it must never make the call
that hurts.** The moment a decision could harm someone, it stops being a feature
and becomes a judgment — and judgments need a name attached.

This is the product's central honesty: **it reproduces a therapist's loyalty, not a
therapist's judgment**, and it is explicit about where that difference begins.

### Why it wins on safety, ergonomics, and trust

**Safety is structural, not policed.** You can't manipulate with a model you don't
hold. You can't leak a profile that's locked and non-queryable. You can't act
against someone via a layer that is, by construction, loyal to them. The dangerous
capabilities aren't restrained — they're _absent by design_.

**Ergonomics: it works for one person on day one.** Your own coaching helps you
immediately. No cold start, no "you only get in if you expose yourself first," no
convincing a hostile ex to join. The other person's model only deepens the
experience; it isn't required for value.

**Trust on both sides, earned not claimed.** The other person experiences you as
steadily clearer and calmer, is never profiled, never targeted, never lied to
(facts stay invariant; only framing adapts). In high-conflict relationships,
**don't badge it** — "he's running me through a bot" is ammunition. Trust comes
from what the system structurally _cannot do_, which no one has to take on faith.

### The moat

You will hold both ends — which means you _could_ trivially build the surveillance
version. The defensible position is the architecturally enforced promise that you
don't:

- Each person's model is loyal to that person and held in a neutral layer.
- It is non-queryable by any human.
- The loyalty test gates everything that crosses.
- The duty of loyalty is enforceable — technically and legally — so a breach is
  something you can be held liable for.

The pitch isn't "we won't weaponize you against each other." It's _"we are
structurally incapable of acting against the person being modeled, and we're
accountable if we do."_ That promise is the trust substrate the entire network runs
on — and it's the one a recipient-profiling competitor can never make, because the
violation is their whole business.

### Risks to watch (managed, not solved)

- **Self-suppression.** It must help you say the hard thing clearly, not help you
  avoid saying it. Anger is sometimes information.
- **Over-smoothing.** It has to sound like you on a good day, not like a managed
  message. Too-perfect calibration trips people's radar.
- **Dependency.** If a relationship only functions with the buffer, it's a crutch.
  The healthy version sometimes gets out of the way.
- **Consent is weaker than authorship.** Auto-built models rest on enrollment,
  review, and deletion — real, but not as strong as a person writing their own
  manual. Say this plainly; don't dress it up.
- **Contextual leakage.** Holding all your relationships at once raises the stakes
  on keeping them separate. Default to walls; never generalize a disclosure across
  contexts without a clear signal.

### The test that governs every future feature

> **Does this serve something both people would knowingly endorse — or one person's
> leverage over the other?**

Clarity, de-escalation, mutual understanding, being reachable well → build it.
"Help me handle them" → that's the poison. Refuse it.

That single question is the whole philosophy.

---

## Pillars 1 & 2 — Multi-channel and the identity/trust graph

These are newer than the fiduciary brief above and are **not yet reconciled** with
its doctrine. Captured here as intent, with the tensions made explicit below.

### Multi-channel

- One layer, many channel adapters (email first, then Slack, then others).
- The neutral layer must sit between a person and each channel. _Open:_ relay
  (server sees content) vs. overlay (client-side coach) — a custody/reach tradeoff.

### Identity & trust graph

- A **server-level graph of connections** maintained across people.
- **Priority from connection depth:** a deeper, higher-frequency _bilateral_
  connection between two people raises how much they should prioritize each other.
- **Trust propagation across edges:** a strong edge between you and me lends some
  trust when you first contact someone close to me (e.g. my wife) — a vouching
  mechanism for cold first contact.

---

## Open architectural questions

The load-bearing tensions surfaced while pressure-testing the three pillars. These
gate the design; resolve before committing to a build.

1. **Is an edge fiduciary material or a forbidden cross-context model?** The hard
   rule forbids assembling a model of anyone else across contexts. A server-level
   bilateral connection graph _is_ a cross-context object about everyone, and
   communication metadata is the most weaponizable social object there is. Either
   edges are co-owned relationship facts that earn a place under the loyalty
   doctrine, or the central graph quietly voids the core safety promise.
2. **Does trust propagation breach the walls?** Vouching ("your edge to me lends you
   trust with my wife") only works if her side learns the you↔me edge exists and is
   strong — disclosing one person's relationship graph to a third party.
3. **Bilaterality requires custody.** Knowing a connection is mutual and
   high-frequency means the server watches both directions of traffic for everyone.
   Even with content gated, that metadata graph is the surveillance substrate the
   moat claims is "absent by design."
4. **Identity resolution is cross-context assembly of _others_.** Linking
   slack-X = email-Y = phone-Z is blessed for _you_ but is the forbidden move when
   done to everyone else to compute their edges.
5. **Custody vs. reach (multi-channel).** Relay (max power, max temptation) vs.
   overlay (less reach, cleaner safety story).

### Candidate resolutions (not yet chosen)

- **One doctrine, not two — make edges fiduciary too.** An edge is co-owned, locked,
  non-queryable, loyal to both endpoints; propagation runs the _same_ loyalty test
  ("does vouching for this stranger serve my wife, or serve the stranger against
  her?"). Unifies all three pillars under the one governing question.
- **No global graph — local trust + explicit vouch.** Priority is computed on your
  device from your own history (no central metadata store); first-contact trust
  requires a mutual contact to _actively_ introduce, rather than ambient
  propagation — consent instead of inference. Trades automatic magic for a clean
  safety story.
