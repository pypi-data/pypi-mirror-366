import orphe

analytics = orphe.Analytics(
    url = "https://example.analytics.orphe.ai",
    token= "your_token"
)

# def callback(value : orphe.AnalyticsValue):
#     print(value.gait.left.quaternion_x)


# analytics.realtime(
#     edge_uuid = "b57cb4be-31f4-4b66-9f6f-9e137c1ff163",
#     callback = callback
# )



analyzed = analytics.load(
    measurement_uuid = "70d1761d-92fd-4d4f-9256-8e5cdf3208df",
    debug=True
)

for pose in analyzed.pose.stored:
    print(pose.position.ankle_left.x);
    print(gait.quaternion_x)
    if gait.analyzed:
        print(gait.stride)

# units = []
# for gait in analyzed.gait.left:
#     if gait.analyzed:
#         unit = orphe.Unit(
#             time = gait.time,
#             id = "Stride2",
#             value = gait.stride + 2,            
#         )

#         units.append(unit)

# analytics.save(
#     measurement_uuid = "0df55937-9cd7-4eb2-a834-71700d669eff",
#     units = units
# )