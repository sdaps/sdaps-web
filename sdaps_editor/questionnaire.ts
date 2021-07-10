export const DEFAULT_COLUMN_COUNT = 1;
export interface EditorLayoutMarker extends OrderedObject {
  type: "LAYOUT";
  columns: 1 | 2 | 3 | 4;
}
export type EditorQuestionnaire = Array<EditorQuestionnaireObject>;
export type EditorQuestionnaireObject = MulticolChild | EditorLayoutMarker;

const MARKER_KEY = -1;

export function questionnaireToEditor(
  questionnaire: Questionnaire
): EditorQuestionnaire {
  let editorQuestionnaire: EditorQuestionnaire = [];

  let lastWasMultiCol = false;

  for (const qObject of questionnaire) {
    if (qObject.type === "multicol") {
      lastWasMultiCol = true;

      editorQuestionnaire.push({
        id: MARKER_KEY,
        type: "LAYOUT",
        columns: qObject.columns,
      });

      for (const innerQObject of qObject.children) {
        editorQuestionnaire.push(innerQObject);
      }
    } else {
      if (lastWasMultiCol) {
        lastWasMultiCol = false;

        editorQuestionnaire.push({
          id: MARKER_KEY,
          type: "LAYOUT",
          columns: DEFAULT_COLUMN_COUNT,
        });
      }

      editorQuestionnaire.push(qObject);
    }
  }

  let highestKey = getHighestKey(editorQuestionnaire);

  for (const key in editorQuestionnaire) {
    const element = editorQuestionnaire[key];

    if (element.id === MARKER_KEY) {
      highestKey += 1;
      editorQuestionnaire[key].id = highestKey;
    }
  }

  return editorQuestionnaire;
}

export function editorToQuestionnaire(
  editorQuestionnaire: EditorQuestionnaire
): Questionnaire {
  let questionnaire: Questionnaire = [];

  let currentMulticol: MulticolQuestionnaireObject | null = null;

  for (const qObject of editorQuestionnaire) {
    if (qObject.type === "LAYOUT") {
      // There is a layout change happening
      if (currentMulticol !== null) {
        // push existing mulitcolumn object to questionnaire
        questionnaire.push(currentMulticol);
      }

      if (qObject.columns === 1) {
        // This is a layout reset. Go back to just adding qObjects
        currentMulticol = null;
      } else {
        currentMulticol = {
          id: qObject.id,
          type: "multicol",
          columns: qObject.columns,
          children: [],
        };
      }
    } else {
      // There is no change in layout
      if (currentMulticol === null) {
        questionnaire.push(qObject);
      } else {
        currentMulticol.children.push(qObject);
      }
    }
  }

  if (currentMulticol !== null) {
    // There is a dangling multicol
    questionnaire.push(currentMulticol);
  }

  return questionnaire;
}

//
export type Questionnaire = Array<QuestionnaireObject>;

export function getHighestKey<T extends OrderedObject>(
  ordered: Array<T>
): number {
  return ordered.reduce((key, section) => Math.max(key, section.id), 0) + 1;
}

//
export type QuestionnaireObject =
  | SectionQuestionnaireObject
  | MulticolQuestionnaireObject
  | TextbodyQuestionnaireObject
  | SinglemarkQuestionnaireObject
  | TextboxQuestionnaireObject
  | MarkgroupQuestionnaireObject
  | ChoicegroupQuestionnaireObject
  | ChoicequestionQuestionnaireObject;

//
export interface OrderedObject {
  id: number;
  type: string;
}

//
export interface SectionQuestionnaireObject extends OrderedObject {
  type: "section";
  title: string;
}

//
export interface MulticolQuestionnaireObject extends OrderedObject {
  type: "multicol";
  columns: 2 | 3 | 4;
  children: Array<MulticolChild>;
}
export type MulticolChild = Exclude<
  QuestionnaireObject,
  MulticolQuestionnaireObject
>;

//
export interface TextbodyQuestionnaireObject extends OrderedObject {
  type: "textbody";
  text: string;
}

//
export interface SinglemarkQuestionnaireObject extends OrderedObject {
  type: "singlemark";
  checkboxcount: number;
  question: string;
  lower: string;
  upper: string;
}

//
export interface TextboxQuestionnaireObject extends OrderedObject {
  type: "textbox";
  expand: boolean;
  height: number;
  question: string;
}

//
export interface MarkgroupQuestionnaireObject extends OrderedObject {
  type: "markgroup";
  heading: string;
  checkboxcount: number;
  children: Array<InnerMarklineQuestionnaireObject>;
}
export interface InnerMarklineQuestionnaireObject extends OrderedObject {
  type: "markline";
  question: string;
  upper: string;
  lower: string;
}

//
export interface ChoicegroupQuestionnaireObject extends OrderedObject {
  type: "choicegroup";
  heading: string;
  children: Array<InnerGroupAddChoice | InnerChoiceLine>;
}
export interface InnerGroupAddChoice extends OrderedObject {
  type: "groupaddchoice";
  choice: string;
}
export interface InnerChoiceLine extends OrderedObject {
  type: "choiceline";
  question: string;
}

//
export interface ChoicequestionQuestionnaireObject extends OrderedObject {
  type: "choicequestion";
  columns: number;
  question: string;
  children: Array<InnerChoiceAnswer | InnerChoiceTextAnswer>;
}
export interface InnerChoiceAnswer extends OrderedObject {
  type: "choiceitem";
  colspan: number;
  answer: string;
}
export interface InnerChoiceTextAnswer extends OrderedObject {
  type: "choiceitemtext";
  colspan: number;
  answer: string;
  height: number;
}
