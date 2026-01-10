# 3D Models for Helmet Camera Mounting
# Mô hình 3D cho lắp đặt Camera Mũ Bảo Hiểm

## Available Models / Mô hình có sẵn

### Camera Mount (camera-mount.stl)

A helmet-mounted camera bracket designed for the ESP32-CAM unit.

Giá đỡ camera gắn trên mũ bảo hiểm được thiết kế cho thiết bị ESP32-CAM.

**Features / Tính năng:**
- Fits standard helmet mounts (GoPro compatible)
- Adjustable angle (0-45 degrees)
- Vibration dampening
- Weatherproof housing
- Easy battery access

**Dimensions / Kích thước:**
- Length: 80mm
- Width: 50mm
- Height: 40mm
- Mounting hole: GoPro standard (3-prong)

**Print Settings / Cài đặt in:**
- Material: PLA or PETG recommended
- Layer height: 0.2mm
- Infill: 20-30%
- Supports: Required for overhang
- Print time: ~2-3 hours

### Battery Holder (battery-holder.stl)

Secure holder for 3S LiPo battery.

Hộp đựng an toàn cho pin LiPo 3S.

**Features:**
- Fits 1500-2000mAh batteries
- Velcro strap slots
- Heat ventilation holes
- Wire routing channels

**Dimensions:**
- Internal: 65mm × 25mm × 35mm
- Wall thickness: 2mm

**Print Settings:**
- Material: PETG (heat resistant)
- Layer height: 0.2mm
- Infill: 30%
- Supports: Minimal

### Electronics Enclosure (electronics-box.stl)

Protective enclosure for ESP32-CAM and power electronics.

Hộp bảo vệ cho ESP32-CAM và điện tử nguồn.

**Features:**
- IP54 water resistance (with gasket)
- Antenna port (SMA cutout)
- Cable glands for wiring
- Mounting holes for internal PCB
- Snap-fit lid

**Dimensions:**
- External: 90mm × 70mm × 35mm
- Internal clearance: 85mm × 65mm × 30mm

**Print Settings:**
- Material: PETG or ABS
- Layer height: 0.2mm
- Infill: 40% (for strength)
- Perimeters: 3-4
- Supports: Required

## 3D Printing Services in Vietnam / Dịch vụ in 3D tại Việt Nam

### Ho Chi Minh City / Thành phố Hồ Chí Minh
- **3D Print VN**: https://3dprint.vn
- **Viet Nam 3D**: https://vietnam3d.vn
- **HCMC Maker Space**: Various services in District 1

### Hanoi / Hà Nội
- **Hanoi 3D Printing**: Search "in 3D Hà Nội"
- **University makerspaces**: HUST, VNU
- **Fab Lab Hanoi**: Community workshop

### Online Marketplaces
- **Shopee**: Search "dịch vụ in 3D"
- **Facebook Groups**: "In 3D Việt Nam"

## Customization / Tùy chỉnh

These models are designed in **OpenSCAD** (open-source parametric CAD):

Các mô hình này được thiết kế trong **OpenSCAD** (CAD tham số mã nguồn mở):

1. **Install OpenSCAD**: https://openscad.org/
2. **Edit .scad file**: Adjust parameters
3. **Export STL**: File → Export → STL
4. **Slice**: Use Cura, PrusaSlicer, etc.

**Example parameters:**
```openscad
// camera-mount.scad
camera_width = 27;      // ESP32-CAM width
camera_length = 40;     // ESP32-CAM length
camera_height = 12;     // ESP32-CAM height
mount_angle = 15;       // Tilt angle in degrees
wall_thickness = 2;     // Box wall thickness
```

## Assembly Instructions / Hướng dẫn lắp ráp

### Step 1: Print Parts
- Print all STL files
- Remove supports carefully
- Sand rough edges if needed

### Step 2: Install Electronics
1. Place ESP32-CAM in enclosure
2. Route antenna cable through port
3. Connect wires for power and battery
4. Secure with small screws or hot glue

### Step 3: Attach Battery
1. Place battery in holder
2. Secure with velcro strap
3. Connect to power system

### Step 4: Mount to Helmet
1. Attach camera mount to helmet
   - Use GoPro adapter if available
   - Or adhesive mount (3M VHB tape)
2. Snap enclosure into mount
3. Adjust angle as needed

### Step 5: Secure Wiring
- Use zip ties for strain relief
- Keep wires away from antenna
- Test all connections

## Design Files / Tệp thiết kế

**Note**: Full OpenSCAD source files (.scad) and STL files will be added to this directory.

**Lưu ý**: Các tệp nguồn OpenSCAD (.scad) và tệp STL đầy đủ sẽ được thêm vào thư mục này.

### Planned Models

- [ ] Receiver station antenna mount
- [ ] Cable organizer clips
- [ ] GoPro mount adapter
- [ ] Protective lens cover

## Contributing / Đóng góp

If you design improvements or new models:

1. Export to STL format
2. Include OpenSCAD source if possible
3. Add photos of printed result
4. Submit pull request with documentation

## License / Giấy phép

All 3D models are released under **Creative Commons Attribution 4.0 (CC BY 4.0)**:
- ✓ Share and adapt freely
- ✓ Commercial use allowed
- ✓ Must give credit

## Safety Warnings / Cảnh báo an toàn

⚠️ **Important:**

1. **Print Quality**: Use appropriate infill for strength
2. **Material Selection**: PETG/ABS for outdoor use
3. **Heat Exposure**: Keep electronics ventilated
4. **Mounting Security**: Test before use to prevent falls
5. **Weatherproofing**: Add silicone/gasket for water resistance

---

**Note:** Actual STL files are not included in this repository but can be generated using the OpenSCAD files or downloaded from community repositories.

**Lưu ý:** Các tệp STL thực tế không được bao gồm trong kho lưu trữ này nhưng có thể được tạo bằng tệp OpenSCAD hoặc tải xuống từ kho lưu trữ cộng đồng.
