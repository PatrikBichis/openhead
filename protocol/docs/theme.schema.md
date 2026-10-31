# Theme

**Title:** Theme

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

**Description:** A theme's `theme.json`: look and idle behaviour of the face. Expressions live in `expressions.json` next to it; images in `assets/`. Lengths are fractions of the screen's shortest side.

| Property                               | Pattern | Type   | Deprecated | Definition                    | Title/Description                                            |
| -------------------------------------- | ------- | ------ | ---------- | ----------------------------- | ------------------------------------------------------------ |
| + [name](#name )                       | No      | string | No         | In common.json#/$defs/name    | Must equal the folder name.                                  |
| + [version](#version )                 | No      | string | No         | In common.json#/$defs/version | Semantic version, MAJOR.MINOR.PATCH.                         |
| - [title](#title )                     | No      | string | No         | -                             | -                                                            |
| - [description](#description )         | No      | string | No         | -                             | -                                                            |
| + [palette](#palette )                 | No      | object | No         | -                             | ThemePalette                                                 |
| + [shapes](#shapes )                   | No      | object | No         | -                             | ThemeShapes                                                  |
| - [layout](#layout )                   | No      | object | No         | -                             | ThemeLayout                                                  |
| - [render](#render )                   | No      | object | No         | -                             | ThemeRender                                                  |
| + [idle](#idle )                       | No      | object | No         | -                             | ThemeIdle                                                    |
| - [envelope](#envelope )               | No      | object | No         | -                             | ThemeEnvelope                                                |
| - [resting_emotion](#resting_emotion ) | No      | string | No         | Same as [name](#name )        | Emotion shown when nothing else is set. Default \`neutral\`. |

## <a name="name"></a>1. Property `Theme > name`

|                |                         |
| -------------- | ----------------------- |
| **Type**       | `string`                |
| **Required**   | Yes                     |
| **Defined in** | common.json#/$defs/name |

**Description:** Must equal the folder name.

| Restrictions                      |                                                                                                             |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z0-9_-]{0,31}$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z0-9_-%5D%7B0%2C31%7D%24) |

## <a name="version"></a>2. Property `Theme > version`

|                |                            |
| -------------- | -------------------------- |
| **Type**       | `string`                   |
| **Required**   | Yes                        |
| **Defined in** | common.json#/$defs/version |

**Description:** Semantic version, MAJOR.MINOR.PATCH.

| Restrictions                      |                                                                                                                       |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[0-9]+\.[0-9]+\.[0-9]+$``` [Test](https://regex101.com/?regex=%5E%5B0-9%5D%2B%5C.%5B0-9%5D%2B%5C.%5B0-9%5D%2B%24) |

## <a name="title"></a>3. Property `Theme > title`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

| Restrictions   |    |
| -------------- | -- |
| **Max length** | 64 |

## <a name="description"></a>4. Property `Theme > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

| Restrictions   |     |
| -------------- | --- |
| **Max length** | 512 |

## <a name="palette"></a>5. Property `Theme > palette`

**Title:** ThemePalette

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | Yes         |
| **Additional properties** | Not allowed |

| Property                     | Pattern | Type   | Deprecated | Definition                 | Title/Description     |
| ---------------------------- | ------- | ------ | ---------- | -------------------------- | --------------------- |
| + [bg](#palette_bg )         | No      | string | No         | In #/$defs/color           | #RRGGBB or #RRGGBBAA. |
| + [sclera](#palette_sclera ) | No      | string | No         | Same as [bg](#palette_bg ) | #RRGGBB or #RRGGBBAA. |
| + [iris](#palette_iris )     | No      | string | No         | Same as [bg](#palette_bg ) | #RRGGBB or #RRGGBBAA. |
| + [pupil](#palette_pupil )   | No      | string | No         | Same as [bg](#palette_bg ) | #RRGGBB or #RRGGBBAA. |
| + [lid](#palette_lid )       | No      | string | No         | Same as [bg](#palette_bg ) | #RRGGBB or #RRGGBBAA. |
| + [mouth](#palette_mouth )   | No      | string | No         | Same as [bg](#palette_bg ) | #RRGGBB or #RRGGBBAA. |
| + [teeth](#palette_teeth )   | No      | string | No         | Same as [bg](#palette_bg ) | #RRGGBB or #RRGGBBAA. |
| + [accent](#palette_accent ) | No      | string | No         | Same as [bg](#palette_bg ) | #RRGGBB or #RRGGBBAA. |

### <a name="palette_bg"></a>5.1. Property `Theme > palette > bg`

|                |               |
| -------------- | ------------- |
| **Type**       | `string`      |
| **Required**   | Yes           |
| **Defined in** | #/$defs/color |

**Description:** #RRGGBB or #RRGGBBAA.

| Restrictions                      |                                                                                                                                              |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^#([0-9a-fA-F]{6}\|[0-9a-fA-F]{8})$``` [Test](https://regex101.com/?regex=%5E%23%28%5B0-9a-fA-F%5D%7B6%7D%7C%5B0-9a-fA-F%5D%7B8%7D%29%24) |

### <a name="palette_sclera"></a>5.2. Property `Theme > palette > sclera`

|                        |                   |
| ---------------------- | ----------------- |
| **Type**               | `string`          |
| **Required**           | Yes               |
| **Same definition as** | [bg](#palette_bg) |

**Description:** #RRGGBB or #RRGGBBAA.

### <a name="palette_iris"></a>5.3. Property `Theme > palette > iris`

|                        |                   |
| ---------------------- | ----------------- |
| **Type**               | `string`          |
| **Required**           | Yes               |
| **Same definition as** | [bg](#palette_bg) |

**Description:** #RRGGBB or #RRGGBBAA.

### <a name="palette_pupil"></a>5.4. Property `Theme > palette > pupil`

|                        |                   |
| ---------------------- | ----------------- |
| **Type**               | `string`          |
| **Required**           | Yes               |
| **Same definition as** | [bg](#palette_bg) |

**Description:** #RRGGBB or #RRGGBBAA.

### <a name="palette_lid"></a>5.5. Property `Theme > palette > lid`

|                        |                   |
| ---------------------- | ----------------- |
| **Type**               | `string`          |
| **Required**           | Yes               |
| **Same definition as** | [bg](#palette_bg) |

**Description:** #RRGGBB or #RRGGBBAA.

### <a name="palette_mouth"></a>5.6. Property `Theme > palette > mouth`

|                        |                   |
| ---------------------- | ----------------- |
| **Type**               | `string`          |
| **Required**           | Yes               |
| **Same definition as** | [bg](#palette_bg) |

**Description:** #RRGGBB or #RRGGBBAA.

### <a name="palette_teeth"></a>5.7. Property `Theme > palette > teeth`

|                        |                   |
| ---------------------- | ----------------- |
| **Type**               | `string`          |
| **Required**           | Yes               |
| **Same definition as** | [bg](#palette_bg) |

**Description:** #RRGGBB or #RRGGBBAA.

### <a name="palette_accent"></a>5.8. Property `Theme > palette > accent`

|                        |                   |
| ---------------------- | ----------------- |
| **Type**               | `string`          |
| **Required**           | Yes               |
| **Same definition as** | [bg](#palette_bg) |

**Description:** #RRGGBB or #RRGGBBAA.

## <a name="shapes"></a>6. Property `Theme > shapes`

**Title:** ThemeShapes

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | Yes         |
| **Additional properties** | Not allowed |

| Property                  | Pattern | Type   | Deprecated | Definition                  | Title/Description                                                                                             |
| ------------------------- | ------- | ------ | ---------- | --------------------------- | ------------------------------------------------------------------------------------------------------------- |
| + [eye](#shapes_eye )     | No      | object | No         | In #/$defs/shape            | One of: a built-in preset, an SVG path in normalised coordinates ([-1, 1] box), or an image from \`assets/\`. |
| + [mouth](#shapes_mouth ) | No      | object | No         | Same as [eye](#shapes_eye ) | One of: a built-in preset, an SVG path in normalised coordinates ([-1, 1] box), or an image from \`assets/\`. |

### <a name="shapes_eye"></a>6.1. Property `Theme > shapes > eye`

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `combining`      |
| **Required**              | Yes              |
| **Additional properties** | Any type allowed |
| **Defined in**            | #/$defs/shape    |

**Description:** One of: a built-in preset, an SVG path in normalised coordinates ([-1, 1] box), or an image from `assets/`.

| One of(Option)                 |
| ------------------------------ |
| [item 0](#shapes_eye_oneOf_i0) |
| [item 1](#shapes_eye_oneOf_i1) |
| [item 2](#shapes_eye_oneOf_i2) |

#### <a name="shapes_eye_oneOf_i0"></a>6.1.1. Property `Theme > shapes > eye > oneOf > item 0`

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

| Property                                 | Pattern | Type             | Deprecated | Definition | Title/Description |
| ---------------------------------------- | ------- | ---------------- | ---------- | ---------- | ----------------- |
| + [preset](#shapes_eye_oneOf_i0_preset ) | No      | enum (of string) | No         | -          | -                 |

##### <a name="shapes_eye_oneOf_i0_preset"></a>6.1.1.1. Property `Theme > shapes > eye > oneOf > item 0 > preset`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | Yes                |

Must be one of:
* "round"
* "almond"
* "slit"
* "pixel"
* "line"

#### <a name="shapes_eye_oneOf_i1"></a>6.1.2. Property `Theme > shapes > eye > oneOf > item 1`

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

| Property                             | Pattern | Type   | Deprecated | Definition | Title/Description |
| ------------------------------------ | ------- | ------ | ---------- | ---------- | ----------------- |
| + [path](#shapes_eye_oneOf_i1_path ) | No      | string | No         | -          | -                 |

##### <a name="shapes_eye_oneOf_i1_path"></a>6.1.2.1. Property `Theme > shapes > eye > oneOf > item 1 > path`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

| Restrictions   |      |
| -------------- | ---- |
| **Min length** | 1    |
| **Max length** | 8192 |

#### <a name="shapes_eye_oneOf_i2"></a>6.1.3. Property `Theme > shapes > eye > oneOf > item 2`

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

| Property                                 | Pattern | Type   | Deprecated | Definition | Title/Description                                                    |
| ---------------------------------------- | ------- | ------ | ---------- | ---------- | -------------------------------------------------------------------- |
| + [image](#shapes_eye_oneOf_i2_image )   | No      | string | No         | -          | -                                                                    |
| - [anchor](#shapes_eye_oneOf_i2_anchor ) | No      | array  | No         | -          | Point in the image placed at the feature centre. Default [0.5, 0.5]. |
| - [scale](#shapes_eye_oneOf_i2_scale )   | No      | number | No         | -          | -                                                                    |

##### <a name="shapes_eye_oneOf_i2_image"></a>6.1.3.1. Property `Theme > shapes > eye > oneOf > item 2 > image`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

| Restrictions                      |                                                                                                                                            |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **Must match regular expression** | ```^assets/[A-Za-z0-9_./-]+\.(png\|svg)$``` [Test](https://regex101.com/?regex=%5Eassets%2F%5BA-Za-z0-9_.%2F-%5D%2B%5C.%28png%7Csvg%29%24) |

##### <a name="shapes_eye_oneOf_i2_anchor"></a>6.1.3.2. Property `Theme > shapes > eye > oneOf > item 2 > anchor`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** Point in the image placed at the feature centre. Default [0.5, 0.5].

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 2                  |
| **Max items**        | 2                  |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be           | Description |
| ----------------------------------------- | ----------- |
| [unit](#shapes_eye_oneOf_i2_anchor_items) | -           |

###### <a name="shapes_eye_oneOf_i2_anchor_items"></a>6.1.3.2.1. Theme > shapes > eye > oneOf > item 2 > anchor > unit

|                |                         |
| -------------- | ----------------------- |
| **Type**       | `number`                |
| **Required**   | No                      |
| **Defined in** | common.json#/$defs/unit |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |
| **Maximum**  | &le; 1 |

##### <a name="shapes_eye_oneOf_i2_scale"></a>6.1.3.3. Property `Theme > shapes > eye > oneOf > item 2 > scale`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

| Restrictions |         |
| ------------ | ------- |
| **Minimum**  | &gt; 0  |
| **Maximum**  | &le; 10 |

### <a name="shapes_mouth"></a>6.2. Property `Theme > shapes > mouth`

|                           |                    |
| ------------------------- | ------------------ |
| **Type**                  | `combining`        |
| **Required**              | Yes                |
| **Additional properties** | Any type allowed   |
| **Same definition as**    | [eye](#shapes_eye) |

**Description:** One of: a built-in preset, an SVG path in normalised coordinates ([-1, 1] box), or an image from `assets/`.

## <a name="layout"></a>7. Property `Theme > layout`

**Title:** ThemeLayout

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

**Description:** Placement relative to the screen centre. Defaults are the engine's.

| Property                              | Pattern | Type   | Deprecated | Definition                                                                     | Title/Description |
| ------------------------------------- | ------- | ------ | ---------- | ------------------------------------------------------------------------------ | ----------------- |
| - [eye_spacing](#layout_eye_spacing ) | No      | number | No         | Same as [shapes_eye_oneOf_i2_anchor_items](#shapes_eye_oneOf_i2_anchor_items ) | -                 |
| - [eye_size](#layout_eye_size )       | No      | number | No         | Same as [shapes_eye_oneOf_i2_anchor_items](#shapes_eye_oneOf_i2_anchor_items ) | -                 |
| - [eye_y](#layout_eye_y )             | No      | number | No         | In common.json#/$defs/signed_unit                                              | -                 |
| - [mouth_width](#layout_mouth_width ) | No      | number | No         | Same as [shapes_eye_oneOf_i2_anchor_items](#shapes_eye_oneOf_i2_anchor_items ) | -                 |
| - [mouth_y](#layout_mouth_y )         | No      | number | No         | Same as [eye_y](#layout_eye_y )                                                | -                 |

### <a name="layout_eye_spacing"></a>7.1. Property `Theme > layout > eye_spacing`

|                        |                                                                       |
| ---------------------- | --------------------------------------------------------------------- |
| **Type**               | `number`                                                              |
| **Required**           | No                                                                    |
| **Same definition as** | [shapes_eye_oneOf_i2_anchor_items](#shapes_eye_oneOf_i2_anchor_items) |

### <a name="layout_eye_size"></a>7.2. Property `Theme > layout > eye_size`

|                        |                                                                       |
| ---------------------- | --------------------------------------------------------------------- |
| **Type**               | `number`                                                              |
| **Required**           | No                                                                    |
| **Same definition as** | [shapes_eye_oneOf_i2_anchor_items](#shapes_eye_oneOf_i2_anchor_items) |

### <a name="layout_eye_y"></a>7.3. Property `Theme > layout > eye_y`

|                |                                |
| -------------- | ------------------------------ |
| **Type**       | `number`                       |
| **Required**   | No                             |
| **Defined in** | common.json#/$defs/signed_unit |

| Restrictions |         |
| ------------ | ------- |
| **Minimum**  | &ge; -1 |
| **Maximum**  | &le; 1  |

### <a name="layout_mouth_width"></a>7.4. Property `Theme > layout > mouth_width`

|                        |                                                                       |
| ---------------------- | --------------------------------------------------------------------- |
| **Type**               | `number`                                                              |
| **Required**           | No                                                                    |
| **Same definition as** | [shapes_eye_oneOf_i2_anchor_items](#shapes_eye_oneOf_i2_anchor_items) |

### <a name="layout_mouth_y"></a>7.5. Property `Theme > layout > mouth_y`

|                        |                        |
| ---------------------- | ---------------------- |
| **Type**               | `number`               |
| **Required**           | No                     |
| **Same definition as** | [eye_y](#layout_eye_y) |

## <a name="render"></a>8. Property `Theme > render`

**Title:** ThemeRender

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

| Property                          | Pattern | Type    | Deprecated | Definition                                                                     | Title/Description                      |
| --------------------------------- | ------- | ------- | ---------- | ------------------------------------------------------------------------------ | -------------------------------------- |
| - [stroke](#render_stroke )       | No      | number  | No         | -                                                                              | Outline width; 0 for none.             |
| - [glow](#render_glow )           | No      | number  | No         | Same as [shapes_eye_oneOf_i2_anchor_items](#shapes_eye_oneOf_i2_anchor_items ) | -                                      |
| - [scanlines](#render_scanlines ) | No      | boolean | No         | -                                                                              | -                                      |
| - [pixelate](#render_pixelate )   | No      | integer | No         | -                                                                              | Pixel block size in points; 0 for off. |

### <a name="render_stroke"></a>8.1. Property `Theme > render > stroke`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Outline width; 0 for none.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |
| **Maximum**  | N/A    |

### <a name="render_glow"></a>8.2. Property `Theme > render > glow`

|                        |                                                                       |
| ---------------------- | --------------------------------------------------------------------- |
| **Type**               | `number`                                                              |
| **Required**           | No                                                                    |
| **Same definition as** | [shapes_eye_oneOf_i2_anchor_items](#shapes_eye_oneOf_i2_anchor_items) |

### <a name="render_scanlines"></a>8.3. Property `Theme > render > scanlines`

|              |           |
| ------------ | --------- |
| **Type**     | `boolean` |
| **Required** | No        |

### <a name="render_pixelate"></a>8.4. Property `Theme > render > pixelate`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | No        |

**Description:** Pixel block size in points; 0 for off.

| Restrictions |         |
| ------------ | ------- |
| **Minimum**  | &ge; 0  |
| **Maximum**  | &le; 64 |

## <a name="idle"></a>9. Property `Theme > idle`

**Title:** ThemeIdle

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | Yes         |
| **Additional properties** | Not allowed |

| Property                                            | Pattern | Type             | Deprecated | Definition                                                                     | Title/Description                                                 |
| --------------------------------------------------- | ------- | ---------------- | ---------- | ------------------------------------------------------------------------------ | ----------------------------------------------------------------- |
| + [blink_interval_ms](#idle_blink_interval_ms )     | No      | array of integer | No         | In #/$defs/range_ms                                                            | [min, max] in milliseconds; a value is drawn uniformly each time. |
| + [blink_duration_ms](#idle_blink_duration_ms )     | No      | integer          | No         | -                                                                              | -                                                                 |
| - [saccade_interval_ms](#idle_saccade_interval_ms ) | No      | array of integer | No         | Same as [blink_interval_ms](#idle_blink_interval_ms )                          | [min, max] in milliseconds; a value is drawn uniformly each time. |
| - [saccade_amplitude](#idle_saccade_amplitude )     | No      | number           | No         | Same as [shapes_eye_oneOf_i2_anchor_items](#shapes_eye_oneOf_i2_anchor_items ) | -                                                                 |
| - [breath_period_ms](#idle_breath_period_ms )       | No      | integer          | No         | -                                                                              | -                                                                 |
| - [breath_amplitude](#idle_breath_amplitude )       | No      | number           | No         | Same as [shapes_eye_oneOf_i2_anchor_items](#shapes_eye_oneOf_i2_anchor_items ) | -                                                                 |

### <a name="idle_blink_interval_ms"></a>9.1. Property `Theme > idle > blink_interval_ms`

|                |                    |
| -------------- | ------------------ |
| **Type**       | `array of integer` |
| **Required**   | Yes                |
| **Defined in** | #/$defs/range_ms   |

**Description:** [min, max] in milliseconds; a value is drawn uniformly each time.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 2                  |
| **Max items**        | 2                  |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be                          | Description |
| -------------------------------------------------------- | ----------- |
| [blink_interval_ms items](#idle_blink_interval_ms_items) | -           |

#### <a name="idle_blink_interval_ms_items"></a>9.1.1. Theme > idle > blink_interval_ms > blink_interval_ms items

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | No        |

| Restrictions |            |
| ------------ | ---------- |
| **Minimum**  | &ge; 0     |
| **Maximum**  | &le; 60000 |

### <a name="idle_blink_duration_ms"></a>9.2. Property `Theme > idle > blink_duration_ms`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

| Restrictions |           |
| ------------ | --------- |
| **Minimum**  | &ge; 30   |
| **Maximum**  | &le; 2000 |

### <a name="idle_saccade_interval_ms"></a>9.3. Property `Theme > idle > saccade_interval_ms`

|                        |                                              |
| ---------------------- | -------------------------------------------- |
| **Type**               | `array of integer`                           |
| **Required**           | No                                           |
| **Same definition as** | [blink_interval_ms](#idle_blink_interval_ms) |

**Description:** [min, max] in milliseconds; a value is drawn uniformly each time.

### <a name="idle_saccade_amplitude"></a>9.4. Property `Theme > idle > saccade_amplitude`

|                        |                                                                       |
| ---------------------- | --------------------------------------------------------------------- |
| **Type**               | `number`                                                              |
| **Required**           | No                                                                    |
| **Same definition as** | [shapes_eye_oneOf_i2_anchor_items](#shapes_eye_oneOf_i2_anchor_items) |

### <a name="idle_breath_period_ms"></a>9.5. Property `Theme > idle > breath_period_ms`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | No        |

| Restrictions |            |
| ------------ | ---------- |
| **Minimum**  | &ge; 500   |
| **Maximum**  | &le; 20000 |

### <a name="idle_breath_amplitude"></a>9.6. Property `Theme > idle > breath_amplitude`

|                        |                                                                       |
| ---------------------- | --------------------------------------------------------------------- |
| **Type**               | `number`                                                              |
| **Required**           | No                                                                    |
| **Same definition as** | [shapes_eye_oneOf_i2_anchor_items](#shapes_eye_oneOf_i2_anchor_items) |

## <a name="envelope"></a>10. Property `Theme > envelope`

**Title:** ThemeEnvelope

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

**Description:** How the speech envelope drives mouth `open`: open = gain * level^gamma, smoothed with attack/release.

| Property                              | Pattern | Type    | Deprecated | Definition | Title/Description |
| ------------------------------------- | ------- | ------- | ---------- | ---------- | ----------------- |
| - [gain](#envelope_gain )             | No      | number  | No         | -          | -                 |
| - [gamma](#envelope_gamma )           | No      | number  | No         | -          | -                 |
| - [attack_ms](#envelope_attack_ms )   | No      | integer | No         | -          | -                 |
| - [release_ms](#envelope_release_ms ) | No      | integer | No         | -          | -                 |

### <a name="envelope_gain"></a>10.1. Property `Theme > envelope > gain`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |
| **Maximum**  | &le; 4 |

### <a name="envelope_gamma"></a>10.2. Property `Theme > envelope > gamma`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | N/A    |
| **Maximum**  | &le; 4 |

### <a name="envelope_attack_ms"></a>10.3. Property `Theme > envelope > attack_ms`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | No        |

| Restrictions |           |
| ------------ | --------- |
| **Minimum**  | &ge; 0    |
| **Maximum**  | &le; 1000 |

### <a name="envelope_release_ms"></a>10.4. Property `Theme > envelope > release_ms`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | No        |

| Restrictions |           |
| ------------ | --------- |
| **Minimum**  | &ge; 0    |
| **Maximum**  | &le; 1000 |

## <a name="resting_emotion"></a>11. Property `Theme > resting_emotion`

|                        |               |
| ---------------------- | ------------- |
| **Type**               | `string`      |
| **Required**           | No            |
| **Same definition as** | [name](#name) |

**Description:** Emotion shown when nothing else is set. Default `neutral`.

----------------------------------------------------------------------------------------------------------------------------
