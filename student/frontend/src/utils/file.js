// 图片添加水印
export const addWatermark = (img, watermark, options = {}) => {
  return new Promise((resolve, reject) => {
    const image = new Image()
    image.crossOrigin = 'Anonymous'
    image.src = img

  const settings = {
    x: 50, // 水印起始X坐标
    y: 50, // 水印起始Y坐标
    color: 'rgba(148, 140, 140, 0.99)',
    spacing: 200, // 水印间距
    rotation: -30, // 水印旋转角度
    fontSize: 18, // 水印字体大小
    ...options
  }

  image.onload = () => {
    const canvas = document.createElement('canvas')
    canvas.width = image.width
    canvas.height = image.height

    const ctx = canvas.getContext('2d')
    ctx.drawImage(image, 0, 0)
    // 设置水印样式
    ctx.font = `${settings.fontSize}px serif`
    ctx.fillStyle = settings.color;

    // 创建水印网格
    for (let row = 0; row < Math.ceil(canvas.height / settings.spacing) + 1; row++) {
      for (let col = 0; col < Math.ceil(canvas.width / settings.spacing) + 1; col++) {
        const centerX = col * settings.spacing + settings.x;
        const centerY = row * settings.spacing + settings.y;
        // 移动到水印中心，旋转，然后绘制
        ctx.save();
        ctx.translate(centerX, centerY);
        ctx.rotate(settings.rotation * Math.PI / 180);
        ctx.fillText(watermark, 0, 0);
        ctx.restore();
      }
    }

    try {
      // const dataURL = canvas.toDataURL('image/png',0.1)
      const dataURL = canvas.toDataURL('image/jpeg')
      resolve(dataURL)
    } catch (e) {
      console.error('toDataURL failed (canvas may be tainted by CORS):', e)
      reject(e)
    }
  }

  image.onerror = (e) => {
    console.error('Image failed to load:', e)
     reject(new Error('图片加载失败'));
  }

  })
}
