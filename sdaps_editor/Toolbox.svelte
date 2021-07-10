<script lang="ts">
  import { Col, Row, Card, CardBody } from "sveltestrap";

  import type { MulticolChild } from "./questionnaire";

  export let tool: MulticolChild["type"];
</script>

<style>
  input[type="radio"] + label {
    color: white;
    line-height: normal;
  }

  input[type="radio"] {
    margin-top: -1px;
    vertical-align: middle;
  }
</style>

<Card color="dark">
  <CardBody>
    <Row>
      <Col>
        <input
          type="radio"
          id="section"
          name="tool"
          value="section"
          bind:group={tool} />
        <label for="section">Section</label>
      </Col>
      <Col>
        <input
          type="radio"
          id="textbody"
          name="tool"
          value="textbody"
          bind:group={tool} />
        <label for="textbody">Textbody</label>
      </Col>
      <Col>
        <input
          type="radio"
          id="textbox"
          name="tool"
          value="textbox"
          bind:group={tool} />
        <label for="textbox">Textbox</label>
      </Col>
      <Col>
        <input
          type="radio"
          id="singlemark"
          name="tool"
          value="singlemark"
          bind:group={tool} />
        <label for="singlemark">Singlemark</label>
      </Col>
      <Col>
        <input
          type="radio"
          id="markgroup"
          name="tool"
          value="markgroup"
          bind:group={tool} />
        <label for="markgroup">Markgroup</label>
      </Col>
      <Col>
        <input
          type="radio"
          id="choicegroup"
          name="tool"
          value="choicegroup"
          bind:group={tool} />
        <label for="choicegroup">Choicegroup</label>
      </Col>
      <Col>
        <input
          type="radio"
          id="choicequestion"
          name="tool"
          value="choicequestion"
          bind:group={tool} />
        <label for="choicequestion">Choicequestion</label>
      </Col>
    </Row>
  </CardBody>
</Card>
