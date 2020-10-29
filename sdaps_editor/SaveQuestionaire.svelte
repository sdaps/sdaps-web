<script>
  import QuestionnaireObject from "./QuestionnaireObject.svelte";

  export let questionnaire = [];

  const basePath = window.location.pathname;
  const questionnairePath = `${basePath}questionnaire/`;

  const BASE_TIMEOUT = 1000;
  let timeout = BASE_TIMEOUT;

  function save() {
    fetch(questionnairePath, {
      method: "POST",
      body: JSON.stringify(questionnaire),
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((res) => {
        if (res.ok) {
          return (timeout = BASE_TIMEOUT);
        } else {
          return (timeout = timeout * 2);
        }
      })
      .catch(() => (timeout = timeout * 2))
      .finally(() => setTimeout(save, timeout));
  }

  save();
</script>

<QuestionnaireObject {questionnaire} />
