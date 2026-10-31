# Hud

**Title:** Hud

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

**Description:** A HUD theme (`face/huds/<name>/hud.json`): what is drawn over the camera view. Text lines are templates: {faces} faces seen, {target} locked face id or NONE, {status} LOCKED or SEARCHING, {id} {conf} {bearing} {elevation} {size} of the locked face, {frame} frame counter, {time} timecode since the view opened, {rand:N} N random digits (change twice a second).

| Property                   | Pattern | Type             | Deprecated | Definition                    | Title/Description                                                                |
| -------------------------- | ------- | ---------------- | ---------- | ----------------------------- | -------------------------------------------------------------------------------- |
| + [name](#name )           | No      | string           | No         | In common.json#/$defs/name    | Lower-case identifier used for themes and emotions.                              |
| + [title](#title )         | No      | string           | No         | -                             | -                                                                                |
| + [version](#version )     | No      | string           | No         | In common.json#/$defs/version | Semantic version, MAJOR.MINOR.PATCH.                                             |
| - [font](#font )           | No      | enum (of string) | No         | -                             | Default mono.                                                                    |
| + [color](#color )         | No      | string           | No         | In #/$defs/color              | Text and boxes.                                                                  |
| - [accent](#accent )       | No      | string           | No         | Same as [color](#color )      | The locked face and highlights.                                                  |
| - [shadow](#shadow )       | No      | string           | No         | Same as [color](#color )      | Glow or shadow behind text and lines.                                            |
| - [tint](#tint )           | No      | object           | No         | -                             | Colour laid over the camera image (works over a native camera view too).         |
| - [scanlines](#scanlines ) | No      | object           | No         | -                             | -                                                                                |
| - [vignette](#vignette )   | No      | number           | No         | -                             | Darker corners.                                                                  |
| - [boxes](#boxes )         | No      | object           | No         | -                             | How every detected face is marked.                                               |
| - [lock](#lock )           | No      | object           | No         | -                             | How the locked face (the largest, or the one \`look_at\` follows) is marked.     |
| - [blocks](#blocks )       | No      | array of object  | No         | -                             | -                                                                                |
| - [boot](#boot )           | No      | object           | No         | -                             | Lines typed out one by one when the view opens, then kept on screen at the left. |

## <a name="name"></a>1. Property `Hud > name`

|                |                         |
| -------------- | ----------------------- |
| **Type**       | `string`                |
| **Required**   | Yes                     |
| **Defined in** | common.json#/$defs/name |

**Description:** Lower-case identifier used for themes and emotions.

| Restrictions                      |                                                                                                             |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z0-9_-]{0,31}$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z0-9_-%5D%7B0%2C31%7D%24) |

## <a name="title"></a>2. Property `Hud > title`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

## <a name="version"></a>3. Property `Hud > version`

|                |                            |
| -------------- | -------------------------- |
| **Type**       | `string`                   |
| **Required**   | Yes                        |
| **Defined in** | common.json#/$defs/version |

**Description:** Semantic version, MAJOR.MINOR.PATCH.

| Restrictions                      |                                                                                                                       |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[0-9]+\.[0-9]+\.[0-9]+$``` [Test](https://regex101.com/?regex=%5E%5B0-9%5D%2B%5C.%5B0-9%5D%2B%5C.%5B0-9%5D%2B%24) |

## <a name="font"></a>4. Property `Hud > font`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

**Description:** Default mono.

Must be one of:
* "mono"
* "sans"

## <a name="color"></a>5. Property `Hud > color`

|                |               |
| -------------- | ------------- |
| **Type**       | `string`      |
| **Required**   | Yes           |
| **Defined in** | #/$defs/color |

**Description:** Text and boxes.

| Restrictions                      |                                                                                             |
| --------------------------------- | ------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^#[0-9a-fA-F]{6}$``` [Test](https://regex101.com/?regex=%5E%23%5B0-9a-fA-F%5D%7B6%7D%24) |

## <a name="accent"></a>6. Property `Hud > accent`

|                        |                 |
| ---------------------- | --------------- |
| **Type**               | `string`        |
| **Required**           | No              |
| **Same definition as** | [color](#color) |

**Description:** The locked face and highlights.

## <a name="shadow"></a>7. Property `Hud > shadow`

|                        |                 |
| ---------------------- | --------------- |
| **Type**               | `string`        |
| **Required**           | No              |
| **Same definition as** | [color](#color) |

**Description:** Glow or shadow behind text and lines.

## <a name="tint"></a>8. Property `Hud > tint`

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

**Description:** Colour laid over the camera image (works over a native camera view too).

| Property                    | Pattern | Type   | Deprecated | Definition               | Title/Description |
| --------------------------- | ------- | ------ | ---------- | ------------------------ | ----------------- |
| + [color](#tint_color )     | No      | string | No         | Same as [color](#color ) | -                 |
| + [opacity](#tint_opacity ) | No      | number | No         | -                        | -                 |

### <a name="tint_color"></a>8.1. Property `Hud > tint > color`

|                        |                 |
| ---------------------- | --------------- |
| **Type**               | `string`        |
| **Required**           | Yes             |
| **Same definition as** | [color](#color) |

### <a name="tint_opacity"></a>8.2. Property `Hud > tint > opacity`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | Yes      |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |
| **Maximum**  | &le; 1 |

## <a name="scanlines"></a>9. Property `Hud > scanlines`

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

| Property                         | Pattern | Type   | Deprecated | Definition | Title/Description     |
| -------------------------------- | ------- | ------ | ---------- | ---------- | --------------------- |
| + [opacity](#scanlines_opacity ) | No      | number | No         | -          | -                     |
| - [spacing](#scanlines_spacing ) | No      | number | No         | -          | Pixels between lines. |

### <a name="scanlines_opacity"></a>9.1. Property `Hud > scanlines > opacity`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | Yes      |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |
| **Maximum**  | &le; 1 |

### <a name="scanlines_spacing"></a>9.2. Property `Hud > scanlines > spacing`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Pixels between lines.

| Restrictions |         |
| ------------ | ------- |
| **Minimum**  | &ge; 2  |
| **Maximum**  | &le; 12 |

## <a name="vignette"></a>10. Property `Hud > vignette`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Darker corners.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |
| **Maximum**  | &le; 1 |

## <a name="boxes"></a>11. Property `Hud > boxes`

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

**Description:** How every detected face is marked.

| Property                 | Pattern | Type             | Deprecated | Definition | Title/Description     |
| ------------------------ | ------- | ---------------- | ---------- | ---------- | --------------------- |
| + [style](#boxes_style ) | No      | enum (of string) | No         | -          | -                     |
| - [width](#boxes_width ) | No      | number           | No         | -          | Line width in points. |
| - [label](#boxes_label ) | No      | string           | No         | -          | -                     |

### <a name="boxes_style"></a>11.1. Property `Hud > boxes > style`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | Yes                |

Must be one of:
* "corners"
* "rect"
* "bracket"
* "none"

### <a name="boxes_width"></a>11.2. Property `Hud > boxes > width`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Line width in points.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | N/A    |
| **Maximum**  | &le; 8 |

### <a name="boxes_label"></a>11.3. Property `Hud > boxes > label`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

| Restrictions   |    |
| -------------- | -- |
| **Max length** | 80 |

## <a name="lock"></a>12. Property `Hud > lock`

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

**Description:** How the locked face (the largest, or the one `look_at` follows) is marked.

| Property                      | Pattern | Type             | Deprecated | Definition | Title/Description                       |
| ----------------------------- | ------- | ---------------- | ---------- | ---------- | --------------------------------------- |
| + [style](#lock_style )       | No      | enum (of string) | No         | -          | -                                       |
| - [label](#lock_label )       | No      | string           | No         | -          | Shown big near the bottom while locked. |
| - [blink_ms](#lock_blink_ms ) | No      | integer          | No         | -          | -                                       |

### <a name="lock_style"></a>12.1. Property `Hud > lock > style`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | Yes                |

Must be one of:
* "crosshair"
* "rect"
* "corners"
* "none"

### <a name="lock_label"></a>12.2. Property `Hud > lock > label`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Shown big near the bottom while locked.

| Restrictions   |    |
| -------------- | -- |
| **Max length** | 40 |

### <a name="lock_blink_ms"></a>12.3. Property `Hud > lock > blink_ms`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | No        |

| Restrictions |           |
| ------------ | --------- |
| **Minimum**  | &ge; 0    |
| **Maximum**  | &le; 5000 |

## <a name="blocks"></a>13. Property `Hud > blocks`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of object` |
| **Required** | No                |

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | N/A                |
| **Max items**        | 8                  |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description |
| ------------------------------- | ----------- |
| [blocks items](#blocks_items)   | -           |

### <a name="blocks_items"></a>13.1. Hud > blocks > blocks items

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

| Property                              | Pattern | Type             | Deprecated | Definition               | Title/Description                                |
| ------------------------------------- | ------- | ---------------- | ---------- | ------------------------ | ------------------------------------------------ |
| + [at](#blocks_items_at )             | No      | enum (of string) | No         | -                        | -                                                |
| + [lines](#blocks_items_lines )       | No      | array of string  | No         | -                        | -                                                |
| - [size](#blocks_items_size )         | No      | number           | No         | -                        | Text size; 1 is about 4.5% of the screen height. |
| - [color](#blocks_items_color )       | No      | string           | No         | Same as [color](#color ) | -                                                |
| - [blink_ms](#blocks_items_blink_ms ) | No      | integer          | No         | -                        | -                                                |

#### <a name="blocks_items_at"></a>13.1.1. Property `Hud > blocks > blocks items > at`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | Yes                |

Must be one of:
* "top-left"
* "top-right"
* "bottom-left"
* "bottom-right"
* "left"

#### <a name="blocks_items_lines"></a>13.1.2. Property `Hud > blocks > blocks items > lines`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of string` |
| **Required** | Yes               |

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | N/A                |
| **Max items**        | 16                 |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be          | Description |
| ---------------------------------------- | ----------- |
| [lines items](#blocks_items_lines_items) | -           |

##### <a name="blocks_items_lines_items"></a>13.1.2.1. Hud > blocks > blocks items > lines > lines items

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

| Restrictions   |    |
| -------------- | -- |
| **Max length** | 80 |

#### <a name="blocks_items_size"></a>13.1.3. Property `Hud > blocks > blocks items > size`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Text size; 1 is about 4.5% of the screen height.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | N/A    |
| **Maximum**  | &le; 3 |

#### <a name="blocks_items_color"></a>13.1.4. Property `Hud > blocks > blocks items > color`

|                        |                 |
| ---------------------- | --------------- |
| **Type**               | `string`        |
| **Required**           | No              |
| **Same definition as** | [color](#color) |

#### <a name="blocks_items_blink_ms"></a>13.1.5. Property `Hud > blocks > blocks items > blink_ms`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | No        |

| Restrictions |           |
| ------------ | --------- |
| **Minimum**  | &ge; 0    |
| **Maximum**  | &le; 5000 |

## <a name="boot"></a>14. Property `Hud > boot`

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

**Description:** Lines typed out one by one when the view opens, then kept on screen at the left.

| Property                            | Pattern | Type            | Deprecated | Definition | Title/Description |
| ----------------------------------- | ------- | --------------- | ---------- | ---------- | ----------------- |
| + [lines](#boot_lines )             | No      | array of string | No         | -          | -                 |
| - [ms_per_line](#boot_ms_per_line ) | No      | integer         | No         | -          | -                 |

### <a name="boot_lines"></a>14.1. Property `Hud > boot > lines`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of string` |
| **Required** | Yes               |

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | N/A                |
| **Max items**        | 24                 |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be  | Description |
| -------------------------------- | ----------- |
| [lines items](#boot_lines_items) | -           |

#### <a name="boot_lines_items"></a>14.1.1. Hud > boot > lines > lines items

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

| Restrictions   |    |
| -------------- | -- |
| **Max length** | 60 |

### <a name="boot_ms_per_line"></a>14.2. Property `Hud > boot > ms_per_line`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | No        |

| Restrictions |           |
| ------------ | --------- |
| **Minimum**  | &ge; 20   |
| **Maximum**  | &le; 2000 |

----------------------------------------------------------------------------------------------------------------------------
