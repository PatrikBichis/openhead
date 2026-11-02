# SpeechSay

**Title:** SpeechSay

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            |                  |

**Description:** Speak with the head's own voice (on-device text to speech), with the mouth moving to the audio and the words as a subtitle. `segments` run in order: `say` speaks text, `emotion` changes the expression right there (the voice follows: brighter for happy, calmer for sad or focused), `action` adds a laugh, a sigh, a pause or a blink, `gesture` is passed on as a cue (`speech` topic) for a body to nod, shake or tilt. Answered at once with the utterance id; progress comes on the `speech` topic (`say_start`, `cue`, `say_end`). By default a new utterance interrupts the one playing. While listening (`speech.listen`), recognition pauses while the head speaks, so it does not hear itself.

| Property                   | Pattern | Type    | Deprecated | Definition | Title/Description                                                                                                      |
| -------------------------- | ------- | ------- | ---------- | ---------- | ---------------------------------------------------------------------------------------------------------------------- |
| + [type](#type )           | No      | string  | No         | -          | Message type, e.g. \`hello\`, \`face.set_emotion\`, \`imu\`.                                                           |
| + [ts](#ts )               | No      | integer | No         | -          | Sender clock in milliseconds since the Unix epoch.                                                                     |
| + [seq](#seq )             | No      | integer | No         | -          | Per-connection, per-direction counter, starting at 0.                                                                  |
| + [id](#id )               | No      | string  | No         | -          | Client-chosen id, echoed in the reply.                                                                                 |
| + [segments](#segments )   | No      | array   | No         | -          | -                                                                                                                      |
| - [voice](#voice )         | No      | string  | No         | -          | A voice identifier, or a language such as \`en-US\` or \`sv-SE\` (the best installed voice for it). Default \`en-US\`. |
| - [rate](#rate )           | No      | number  | No         | -          | Speaking rate relative to normal (1).                                                                                  |
| - [pitch](#pitch )         | No      | number  | No         | -          | Pitch relative to normal (1).                                                                                          |
| - [subtitle](#subtitle )   | No      | boolean | No         | -          | Show the words on screen as they are spoken. Default true.                                                             |
| - [interrupt](#interrupt ) | No      | boolean | No         | -          | Stop what is being said now (default true); false queues after it.                                                     |

## <a name="type"></a>1. Property `Envelope > type`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Message type, e.g. `hello`, `face.set_emotion`, `imu`.

| Restrictions                      |                                                                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z_]*(\.[a-z][a-z_]*)?$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z_%5D%2A%28%5C.%5Ba-z%5D%5Ba-z_%5D%2A%29%3F%24) |

## <a name="ts"></a>2. Property `Envelope > ts`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Sender clock in milliseconds since the Unix epoch.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="seq"></a>3. Property `Envelope > seq`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Per-connection, per-direction counter, starting at 0.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="id"></a>4. Property `Command > id`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Client-chosen id, echoed in the reply.

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 1  |
| **Max length** | 64 |

## <a name="segments"></a>5. Property `SpeechSay > segments`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | Yes     |

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 1                  |
| **Max items**        | 200                |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be     | Description |
| ----------------------------------- | ----------- |
| [SpeechSaySegment](#segments_items) | -           |

### <a name="segments_items"></a>5.1. SpeechSay > segments > SpeechSaySegment

**Title:** SpeechSaySegment

|                           |                 |
| ------------------------- | --------------- |
| **Type**                  | `combining`     |
| **Required**              | No              |
| **Additional properties** | Not allowed     |
| **Defined in**            | #/$defs/segment |

| Property                                  | Pattern | Type             | Deprecated | Definition                    | Title/Description                                                                                                                                                       |
| ----------------------------------------- | ------- | ---------------- | ---------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| - [say](#segments_items_say )             | No      | string           | No         | -                             | Text to speak.                                                                                                                                                          |
| - [emotion](#segments_items_emotion )     | No      | string           | No         | In ../common.json#/$defs/name | An expression from \`face.list\`; it holds until the next one.                                                                                                          |
| - [intensity](#segments_items_intensity ) | No      | number           | No         | In ../common.json#/$defs/unit | With \`emotion\`; default 1.                                                                                                                                            |
| - [action](#segments_items_action )       | No      | enum (of string) | No         | -                             | \`laugh\`: a short laugh with the laughing expression, then back to the expression before. \`sigh\`: a sigh. \`pause\`: silence for \`seconds\`. \`blink\`: blink once. |
| - [seconds](#segments_items_seconds )     | No      | number           | No         | -                             | With \`action: pause\`; default 0.5.                                                                                                                                    |
| - [gesture](#segments_items_gesture )     | No      | enum (of string) | No         | -                             | Sent as a \`cue\` on the \`speech\` topic at this point, for a body that moves the head.                                                                                |

| One of(Option)                     |
| ---------------------------------- |
| [item 0](#segments_items_oneOf_i0) |
| [item 1](#segments_items_oneOf_i1) |
| [item 2](#segments_items_oneOf_i2) |
| [item 3](#segments_items_oneOf_i3) |

#### <a name="segments_items_oneOf_i0"></a>5.1.1. Property `SpeechSay > segments > SpeechSaySegment > oneOf > item 0`

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

##### <a name="autogenerated_heading_2"></a>5.1.1.1. The following properties are required
* say

#### <a name="segments_items_oneOf_i1"></a>5.1.2. Property `SpeechSay > segments > SpeechSaySegment > oneOf > item 1`

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

##### <a name="autogenerated_heading_3"></a>5.1.2.1. The following properties are required
* emotion

#### <a name="segments_items_oneOf_i2"></a>5.1.3. Property `SpeechSay > segments > SpeechSaySegment > oneOf > item 2`

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

##### <a name="autogenerated_heading_4"></a>5.1.3.1. The following properties are required
* action

#### <a name="segments_items_oneOf_i3"></a>5.1.4. Property `SpeechSay > segments > SpeechSaySegment > oneOf > item 3`

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

##### <a name="autogenerated_heading_5"></a>5.1.4.1. The following properties are required
* gesture

#### <a name="segments_items_say"></a>5.1.5. Property `SpeechSay > segments > SpeechSaySegment > say`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Text to speak.

| Restrictions   |      |
| -------------- | ---- |
| **Min length** | 1    |
| **Max length** | 2000 |

#### <a name="segments_items_emotion"></a>5.1.6. Property `SpeechSay > segments > SpeechSaySegment > emotion`

|                |                            |
| -------------- | -------------------------- |
| **Type**       | `string`                   |
| **Required**   | No                         |
| **Defined in** | ../common.json#/$defs/name |

**Description:** An expression from `face.list`; it holds until the next one.

| Restrictions                      |                                                                                                             |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z0-9_-]{0,31}$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z0-9_-%5D%7B0%2C31%7D%24) |

#### <a name="segments_items_intensity"></a>5.1.7. Property `SpeechSay > segments > SpeechSaySegment > intensity`

|                |                            |
| -------------- | -------------------------- |
| **Type**       | `number`                   |
| **Required**   | No                         |
| **Defined in** | ../common.json#/$defs/unit |

**Description:** With `emotion`; default 1.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |
| **Maximum**  | &le; 1 |

#### <a name="segments_items_action"></a>5.1.8. Property `SpeechSay > segments > SpeechSaySegment > action`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

**Description:** `laugh`: a short laugh with the laughing expression, then back to the expression before. `sigh`: a sigh. `pause`: silence for `seconds`. `blink`: blink once.

Must be one of:
* "laugh"
* "sigh"
* "pause"
* "blink"

#### <a name="segments_items_seconds"></a>5.1.9. Property `SpeechSay > segments > SpeechSaySegment > seconds`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** With `action: pause`; default 0.5.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |
| **Maximum**  | &le; 5 |

#### <a name="segments_items_gesture"></a>5.1.10. Property `SpeechSay > segments > SpeechSaySegment > gesture`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

**Description:** Sent as a `cue` on the `speech` topic at this point, for a body that moves the head.

Must be one of:
* "nod"
* "shake"
* "tilt"

## <a name="voice"></a>6. Property `SpeechSay > voice`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** A voice identifier, or a language such as `en-US` or `sv-SE` (the best installed voice for it). Default `en-US`.

| Restrictions   |     |
| -------------- | --- |
| **Min length** | 2   |
| **Max length** | 128 |

## <a name="rate"></a>7. Property `SpeechSay > rate`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Speaking rate relative to normal (1).

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | N/A    |
| **Maximum**  | &le; 2 |

## <a name="pitch"></a>8. Property `SpeechSay > pitch`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Pitch relative to normal (1).

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | N/A    |
| **Maximum**  | &le; 2 |

## <a name="subtitle"></a>9. Property `SpeechSay > subtitle`

|              |           |
| ------------ | --------- |
| **Type**     | `boolean` |
| **Required** | No        |

**Description:** Show the words on screen as they are spoken. Default true.

## <a name="interrupt"></a>10. Property `SpeechSay > interrupt`

|              |           |
| ------------ | --------- |
| **Type**     | `boolean` |
| **Required** | No        |

**Description:** Stop what is being said now (default true); false queues after it.

----------------------------------------------------------------------------------------------------------------------------
