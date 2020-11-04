<script lang="ts">
  import SaveQuestionaire from "./SaveQuestionaire.svelte";
  import { Spinner } from "sveltestrap";

  const basePath = window.location.pathname;
  const questionnairePath = `${basePath}questionnaire/`;

  const questionnaireRequest = fetch(questionnairePath)
    .then((res) => res.json())
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
