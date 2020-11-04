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
  .markgroupChild {
    margin-top: 10px;
  }

  summary {
    margin-bottom: 0.6em;
  }
</style>

<div class="input-group mb-3">
  <div class="input-group-prepend">
    <label class="input-group-text" for="inputGroupSelect01">Heading:</label>
  </div>
  <input
    type="text"
    class="form-control"
    placeholder=""
    aria-label="Example text with button addon"
    bind:value={markgroup.heading} />
  <div class="input-group-prepend">
    <label class="input-group-text" for="inputGroupSelect01">Number of
      checkboxes:</label>
  </div>
  <input
    class="form-control"
    placeholder=""
    aria-label="Example text with button addon"
    type="number"
    min="2"
    max="10"
    step="1"
    bind:value={markgroup.checkboxcount} />
</div>
<details>
  <summary>Marklines</summary>
  <p>
    <button class="btn btn-sm btn-success" on:click={() => addSection(-1)}>Add
      markline</button>
  </p>
  <div
    class="dropZone"
    use:dndzone={{ items: markgroup.children, flipDurationMs, dropTargetStyle: { outline: 'solid 2px blue' }, type: 'markgroup' }}
    on:consider={handleDndConsider}
    on:finalize={handleDndFinalize}>
    {#each markgroup.children as markline, idx (markline.id)}
      <div class="markgroupChild card">
        <div class="card-body">
          <div class="input-group mb-3">
            <div class="input-group-prepend">
              <span class="input-group-text" id="basic-addon3">Question</span>
            </div>
            <input
              type="text"
              class="form-control"
              id="basic-url"
              aria-describedby="basic-addon3"
              bind:value={markline.question} />
          </div>
          <div class="input-group mb-3">
            <div class="input-group-prepend">
              <span class="input-group-text" id="basic-addon3">Lower</span>
            </div>
            <input
              type="text"
              class="form-control"
              id="basic-url"
              aria-describedby="basic-addon3"
              bind:value={markline.lower} />
            <div class="input-group-prepend">
              <span class="input-group-text" id="basic-addon3">Upper</span>
            </div>
            <input
              type="text"
              class="form-control"
              id="basic-url"
              aria-describedby="basic-addon3"
              bind:value={markline.upper} />
          </div>
          <div class="btn-group-vertical" role="group">
            <button
              class="btn btn-sm btn-danger"
              on:click={() => deleteSection(idx)}>Remove</button>
          </div>
        </div>
      </div>
    {/each}
  </div>
</details>
