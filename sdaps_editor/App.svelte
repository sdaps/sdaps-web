<script lang="ts">
  import SaveQuestionaire from "./SaveQuestionaire.svelte";
  import { Spinner } from "sveltestrap";
  import { questionnaireToEditor } from "./questionnaire";

  const basePath = window.location.pathname;
  const questionnairePath = `${basePath}questionnaire/`;

  const questionnaireRequest = fetch(questionnairePath)
    .then((res) => res.json())
    .then((jsonQ) => questionnaireToEditor(jsonQ))
    .catch(() => []);
</script>

<main>
  {#await questionnaireRequest}
    <center>
      <Spinner color="dark" />
    </center>
  {:then questionnaire}
    <SaveQuestionaire {questionnaire} />
  {/await}
</main>
