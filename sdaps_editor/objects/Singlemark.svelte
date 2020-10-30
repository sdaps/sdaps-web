<script lang="ts">
  import type { SinglemarkQuestionnaireObject } from "../questionnaire";

  export let singlemark: SinglemarkQuestionnaireObject;
</script>

<label>
  Number of checkboxes:
  <input
    type="number"
    min="2"
    max="10"
    step="1"
    bind:value={singlemark.checkboxcount} />
</label>

<label> Question: <input type="text" bind:value={singlemark.question} /></label>

<label> Upper: <input type="text" bind:value={singlemark.upper} /></label>

<label> Lower: <input type="text" bind:value={singlemark.lower} /></label>
