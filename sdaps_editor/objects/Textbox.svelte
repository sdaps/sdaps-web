<script lang="ts">
  import type { TextboxQuestionnaireObject } from "../questionnaire";

  export let textbox: TextboxQuestionnaireObject;
</script>

<style>
  textarea {
    border: solid 1px black;
    width: 100%;
    resize: none;
  }
</style>

<label> Question: <input type="text" bind:value={textbox.question} /></label>

<label>Expand: <input type="checkbox" bind:checked={textbox.expand} /></label>

<label>
  Height:
  <input
    type="number"
    min="1"
    max="12"
    step="1"
    disabled={textbox.expand}
    bind:value={textbox.height} />
</label>

<textarea
  name="answer"
  rows={textbox.height * window.devicePixelRatio}
  disabled />
