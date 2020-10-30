<script lang="ts">
  import type { TextbodyQuestionnaireObject } from "../questionnaire";

  export let textbody: TextbodyQuestionnaireObject;
</script>

<label>Textbody: <input type="text" bind:value={textbody.text} /></label>
