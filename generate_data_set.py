from PIL import Image, ImageDraw, ImageFont
import random, os, requests, time
from io import BytesIO
import imagehash
from tqdm import tqdm
import threading

colors = [
    "#ff008a",
    "#ff005a",
    "#ff0026",
    "#ff3f00",
    "#ff6900",
    "#ff7a00",
    "#ff8900",
    "#ff9900",
    "#ffa800",
    "#ffba00",
    "#ffcf00",
    "#ffe700",
    "#fbff00",
    "#caff00",
    "#53ff00",
    "#00ff69",
    "#00ffa7",
    "#00ffc9",
    "#00ffdc",
    "#00ffed",
    "#00ffff",
    "#00ecff",
    "#00d1ff",
    "#00adff",
    "#0a53ff",
    "#838fff",
    "#7300ff",
    "#8200ff",
    "#8d00ff",
    "#9800ff",
    "#a200ff",
    "#b000ff",
    "#c900ff",
    "#ee00ff",
    "#ff00f3",
    "#ff00bb",
]


def render_annotations(original_img, annotations):
    # 创建一个新图像以保留原始图像不变
    annotated_img = original_img.copy()
    draw = ImageDraw.Draw(annotated_img)

    # 遍历标注并在图像上绘制框
    for xmin, ymin, xmax, ymax, label in annotations:
        # 绘制矩形框
        draw.rectangle([(xmin, ymin), (xmax, ymax)], outline="red", width=2)
        # 可以在这里添加文本绘制代码，例如标签名称
    annotated_img.save("check_annotated_image.png")
    # return annotated_img


def get_random_common_chars(num_chars):
    # 从文件中读取汉字
    with open("common_zh_char.txt", "r", encoding="utf-8") as file:
        chars = file.readlines()

    # 移除换行符并随机选择字符
    chars = [char.strip() for char in chars]
    selected_chars = [random.choice(chars) for _ in range(num_chars)]

    return selected_chars


def fetch_random_image():
    # 使用随机图片API获取图片
    # 注意：这个API可能随时变更或失效，您可能需要替换为其他可靠的图片源
    url = "https://source.unsplash.com/random/344x344"
    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            return image
        except requests.RequestException as e:
            # print(f"Error fetching image: {e}")
            # print("Retrying...")
            time.sleep(5)


def random_chars():
    num_chars = random.randint(2, 4)
    chars = get_random_common_chars(num_chars)
    return chars


def target_img(colors, font_file, chars):
    # 图像尺寸
    img_size = 344

    # 创建一个白色背景图像
    image = fetch_random_image()

    # 存储字符位置，确保不重叠
    positions = []
    exclude_range_limit = 6
    annotations = []
    for char in chars:
        # 随机选择字体和大小

        font_size = random.choice([24, 36])
        font = ImageFont.truetype(os.path.join("fonts/main", font_file), font_size)

        char_image_size = font_size
        char_image = Image.new(
            "RGBA", (char_image_size, char_image_size), (255, 255, 255, 0)
        )
        char_draw = ImageDraw.Draw(char_image)

        # 选择颜色
        fill_color = random.choice(colors)
        # 将颜色转换为RGB格式
        fill_color_rgb = tuple(
            int(fill_color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)
        )
        # 获取选中颜色的索引
        fill_color_index = colors.index(fill_color)

        # 计算需要排除的索引范围
        exclude_range = range(
            max(0, fill_color_index - exclude_range_limit),
            min(len(colors), fill_color_index + exclude_range_limit),
        )

        # 创建一个新的颜色列表，排除掉指定范围内的颜色
        new_colors = [color for i, color in enumerate(colors) if i not in exclude_range]

        # 随机选择高对比度颜色
        contrast_colors = [color for color in new_colors if color != fill_color]
        contrast_color = random.choice(contrast_colors)
        contrast_color_rgb = tuple(
            int(contrast_color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)
        )

        idx = colors.index(contrast_color)
        exclude_range = range(
            max(0, idx - exclude_range_limit),
            min(len(colors), idx + exclude_range_limit),
        )
        new_colors = [
            color for i, color in enumerate(new_colors) if i not in exclude_range
        ]

        second_contrast_colors = [
            color
            for color in new_colors
            if color != fill_color and color != contrast_color
        ]
        second_contrast_color = random.choice(second_contrast_colors)
        second_contrast_color_rgb = tuple(
            int(second_contrast_color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)
        )

        # 随机放置字符，确保不重叠
        inner_padding = 8
        while True:
            x = random.randint(inner_padding, img_size - font_size - inner_padding)
            y = random.randint(inner_padding, img_size - font_size - inner_padding)
            new_char_bound = (x, y, x + font_size, y + font_size)

            overlap = False
            for existing_char_bound in positions:
                # 检查新字符是否与现有字符重叠
                if (
                    new_char_bound[0] < existing_char_bound[2]
                    and new_char_bound[2] > existing_char_bound[0]
                    and new_char_bound[1] < existing_char_bound[3]
                    and new_char_bound[3] > existing_char_bound[1]
                ):
                    overlap = True
                    break

            if not overlap:
                break

        positions.append(new_char_bound)

        # 绘制字符及其阴影
        text_position = (
            char_image_size // 2 - font_size // 2,
            char_image_size // 2 - font_size // 2,
        )
        # 阴影
        char_draw.text(
            (text_position[0] + 1, text_position[1] + 1),
            char,
            font=font,
            fill=second_contrast_color_rgb,
        )
        # 文字
        char_draw.text(text_position, char, font=font, fill=fill_color_rgb)

        # 随机旋转字符
        angle = random.choice([-35, -30, -15, 0, 15, 30, 35])
        rotated_char_image = char_image.rotate(angle, expand=1)

        # 计算字符图像在背景上的位置，同时考虑内边距
        padding = 10
        paste_x = max(
            padding,
            min(
                x - rotated_char_image.width // 2 + font_size,
                img_size - rotated_char_image.width - padding,
            ),
        )
        paste_y = max(
            padding,
            min(
                y - rotated_char_image.height // 2 + font_size,
                img_size - rotated_char_image.height - padding,
            ),
        )
        image.paste(rotated_char_image, (paste_x, paste_y), rotated_char_image)

        # 记录标注数据
        xmin = paste_x
        ymin = paste_y
        xmax = xmin + rotated_char_image.width
        ymax = ymin + rotated_char_image.height
        annotations.append((xmin, ymin, xmax, ymax, "target"))

        cropped_image = image.crop((xmin, ymin, xmax, ymax))
        hash_value = imagehash.phash(cropped_image)
        if not os.path.exists(f"capta_siamese_data_set/{char}"):
            os.makedirs(f"capta_siamese_data_set/{char}")
        cropped_image.save(f"capta_siamese_data_set/{char}/{hash_value}.png")

        # print(
        #     f"Character: {char}, Font size: {font_size}, Color: {fill_color}:{colors.index(fill_color)}/{contrast_color}:{colors.index(contrast_color)}/{second_contrast_color}:{colors.index(second_contrast_color)}, Position: ({x}, {y}), "
        # )

    return image, annotations


def chor_img(font_file, chars):
    font_size = 20
    font = ImageFont.truetype(os.path.join("fonts/intro", font_file), font_size)

    chor_img = Image.new("RGB", (150, 40), color="white")
    chor_draw = ImageDraw.Draw(chor_img)

    current_x = 4  # 初始X坐标位置
    annotations = []  # 用于存储标注信息

    for text in chars:
        # 计算字符尺寸
        text_width, text_height = font.getsize(text)
        # text_bbox = font.getbbox(text)

        # # 计算文字的宽度和高度
        # text_width = text_bbox[2] - text_bbox[0]
        # text_height = text_bbox[3] - text_bbox[1]

        temp_img = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)

        # 绘制黑色边框
        border_offset = 1
        for dx in range(-border_offset, border_offset + 1):
            for dy in range(-border_offset, border_offset + 1):
                temp_draw.text((dx, dy), text, font=font, fill="black")

        # 在黑色边框上绘制白色文字
        temp_draw.text((0, 0), text, font=font, fill="white")

        # 随机旋转角度
        angle = random.choice([-35, -30, -15, 0, 15, 30, 35])
        rotated_temp_img = temp_img.rotate(angle, expand=True)

        # 计算旋转后字符图像在背景图像上的位置
        y_position = (chor_img.height - rotated_temp_img.height) // 2

        # 将旋转后的字符图像粘贴到背景图像上
        chor_img.paste(rotated_temp_img, (current_x, y_position), rotated_temp_img)

        # 记录标注数据
        xmin = current_x + 1
        ymin = y_position + 1
        xmax = xmin + rotated_temp_img.width - 2
        ymax = ymin + rotated_temp_img.height - 2
        annotations.append((xmin, ymin, xmax, ymax, "chor"))

        cropped_image = chor_img.crop((xmin, ymin, xmax, ymax))
        hash_value = imagehash.phash(cropped_image)
        if not os.path.exists(f"capta_siamese_data_set/{text}"):
            os.makedirs(f"capta_siamese_data_set/{text}")
        cropped_image.save(f"capta_siamese_data_set/{text}/{hash_value}.png")

        # 更新X坐标位置
        current_x += text_width + 4  # 添加字符间距

        # print("annotations: ", annotations)

        # 如果下一个字符将超出图像宽度，则停止
        if current_x >= 150 - 10:  # 10为右边距
            break

    return chor_img, annotations


def final_img(target_img, target_annotations, chor_img, chor_annotations, name):
    updated_annotations = []

    final_img = Image.new("RGB", (344, 384), color="black")
    x = (final_img.width - target_img.width) // 2
    y = 0  # 紧贴上边缘
    final_img.paste(target_img, (x, y))

    for xmin, ymin, xmax, ymax, label in target_annotations:
        # 更新坐标
        xmin_updated = xmin + x
        ymin_updated = ymin + y
        xmax_updated = xmax + x
        ymax_updated = ymax + y

        updated_annotations.append(
            (xmin_updated, ymin_updated, xmax_updated, ymax_updated, label)
        )

    # 将intro_img贴在底部左边缘位置
    x_chor = 0  # 紧贴左边缘
    y_chor = final_img.height - chor_img.height  # 紧贴下边缘

    for xmin, ymin, xmax, ymax, label in chor_annotations:
        # 更新坐标
        xmin_updated = xmin + x_chor
        ymin_updated = ymin + y_chor
        xmax_updated = xmax + x_chor
        ymax_updated = ymax + y_chor

        updated_annotations.append(
            (xmin_updated, ymin_updated, xmax_updated, ymax_updated, label)
        )

    # final_annotations: class_id center_x center_y width height

    final_img.paste(chor_img, (x_chor, y_chor))
    render_annotations(final_img, updated_annotations)
    final_img.save(f"{name}.png")
    return final_img, updated_annotations


def save_annotations_to_txt(annotations, file_path, labels, final_img):
    with open(file_path, "w") as f:
        for xmin, ymin, xmax, ymax, label in annotations:
            # 计算中心点坐标和宽高
            center_x = (xmin + xmax) / 2 / final_img.width
            center_y = (ymin + ymax) / 2 / final_img.height
            width = (xmax - xmin) / final_img.width
            height = (ymax - ymin) / final_img.height
            # 获取类别索引
            class_id = labels.index(label)

            # 写入文件
            f.write(
                f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n"
            )


# for i in tqdm(range(10000)):
#     chars = random_chars()
#     name = f"capta_data_set/{i}"
#     # print(f"Characters: {chars}")
#     font_files = os.listdir("fonts/main")
#     font_files = [f for f in font_files if f.endswith(".ttf") or f.endswith(".otf")]
#     font = random.choice(font_files)

#     target_image_file, target_anno = target_img(colors, font, chars)

#     font_files = os.listdir("fonts/intro")
#     font_files = [f for f in font_files if f.endswith(".ttf") or f.endswith(".otf")]
#     font = random.choice(font_files)

#     chor_image_file, chor_anno = chor_img(font, chars)

#     fin_img, fin_anno = final_img(
#         target_image_file, target_anno, chor_image_file, chor_anno, name
#     )
#     save_annotations_to_txt(fin_anno, f"{name}.txt", ["target", "chor"], fin_img)


def process_image(i):
    # 模拟您的图像处理和保存操作
    chars = random_chars()
    name = f"capta_data_set/{i}"

    font_files = os.listdir("fonts/target")
    font_files = [f for f in font_files if f.endswith(".ttf") or f.endswith(".otf")]
    font = random.choice(font_files)

    target_image_file, target_anno = target_img(colors, font, chars)

    font_files = os.listdir("fonts/chor")
    font_files = [f for f in font_files if f.endswith(".ttf") or f.endswith(".otf")]
    font = random.choice(font_files)

    chor_image_file, chor_anno = chor_img(font, chars)

    fin_img, fin_anno = final_img(
        target_image_file, target_anno, chor_image_file, chor_anno, name
    )
    save_annotations_to_txt(fin_anno, f"{name}.txt", ["target", "chor"], fin_img)


def main():
    threads = []

    for i in tqdm(range(3000)):
        # 检查当前活跃线程数量
        while threading.active_count() >= 100:
            # 如果活跃线程数量达到或超过100，等待一段时间
            time.sleep(1)

        # 创建并启动新线程
        t = threading.Thread(target=process_image, args=(i,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
