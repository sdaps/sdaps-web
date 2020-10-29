<script>
  import QuestionnaireObject from "./QuestionnaireObject.svelte";

  export let questionnaire = [];

  const basePath = window.location.pathname;
  const questionnairePath = `${basePath}questionnaire/`;

  const BASE_TIMEOUT = 1000;
  let timeout = BASE_TIMEOUT;

  function getCookie(name) {
    if (!document.cookie) {
      return null;
    }

    const xsrfCookies = document.cookie
      .split(";")
      .map((c) => c.trim())
      .filter((c) => c.startsWith(name + "="));

    if (xsrfCookies.length === 0) {
      return null;
    }
    return decodeURIComponent(xsrfCookies[0].split("=")[1]);
  }

  function save() {
    const csrfToken = getCookie("csrftoken");

    fetch(questionnairePath, {
      method: "POST",
      body: JSON.stringify(questionnaire),
      credentials: "include",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
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
