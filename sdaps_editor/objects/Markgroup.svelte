<script lang="ts">
  import { dndzone } from "svelte-dnd-action";
  import { updateKey } from "../keyTracker";

  import type { MarkgroupQuestionnaireObject } from "../questionnaire";
  import { getHighestKey } from "../questionnaire";

  export let markgroup: MarkgroupQuestionnaireObject;

  const key = getHighestKey(markgroup.children);
  const listKey = updateKey(key);

  // Add and remove
  function addSection(idx: number) {
    const startIdx = idx + 1;

    $listKey += 1;

    markgroup.children.splice(startIdx, 0, {
      id: $listKey,
      type: "markline",
      question: "Question",
      upper: "upper",
      lower: "lower",
    });

    markgroup.children = markgroup.children;
  }

  function deleteSection(idx: number) {
    const startIdx = idx;

    markgroup.children.splice(startIdx, 1);

    markgroup.children = markgroup.children;
  }

  // Drag and drop

  const flipDurationMs = 50;

  function handleDndConsider(e) {
    markgroup.children = e.detail.items;
  }

  function handleDndFinalize(e) {
    markgroup.children = e.detail.items;
  }
</script>

<style>
  .dropZone {
    min-height: 3em;
  }
</style>

<label> Heading: <input type="text" bind:value={markgroup.heading} /></label>

<label>
  Number of checkboxes:
  <input
    type="number"
    min="2"
    max="10"
    step="1"
    bind:value={markgroup.checkboxcount} />
</label>

<p><button on:click={() => addSection(-1)}>Add</button></p>
<div
  class="dropZone"
  use:dndzone={{ items: markgroup.children, flipDurationMs, dropTargetStyle: { outline: 'solid 2px blue' }, type: 'markgroup' }}
  on:consider={handleDndConsider}
  on:finalize={handleDndFinalize}>
  {#each markgroup.children as markline, idx (markline.id)}
    <div>
      <p>
        <label>
          Question:
          <input type="text" bind:value={markline.question} /></label>

        <label> Upper: <input type="text" bind:value={markline.upper} /></label>

        <label> Lower: <input type="text" bind:value={markline.lower} /></label>

        <button on:click={() => deleteSection(idx)}>Remove</button>
      </p>
      <p><button on:click={() => addSection(idx)}>Add</button></p>
    </div>
  {/each}
</div>
