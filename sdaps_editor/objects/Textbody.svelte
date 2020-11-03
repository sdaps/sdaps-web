<script lang="ts">
  import type { TextbodyQuestionnaireObject } from "../questionnaire";

  export let textbody: TextbodyQuestionnaireObject;
</script>

<div class="form-group">
  <textarea class="form-control" id="exampleFormControlTextarea1" rows="3" bind:value={textbody.text}></textarea>
</div>
