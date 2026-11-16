Imports System
Imports System.Globalization
Imports System.IO
Imports NXOpen
Imports NXOpen.Features

Module NXCalibration
    Private Sub AddGauge(part As Part, name As String, point As Point3d, x As String, y As String, z As String)
        Dim builder = part.Features.CreateBlockFeatureBuilder(Nothing)
        Try
            builder.Type = BlockFeatureBuilder.Types.OriginAndEdgeLengths
            builder.SetOriginAndLengths(point, x, y, z)
            Dim feature = CType(builder.CommitFeature(), BodyFeature)
            feature.SetName(name)
            feature.GetBodies()(0).SetName(name)
        Finally
            builder.Destroy()
        End Try
    End Sub

    Sub Main()
        Dim root = Environment.GetEnvironmentVariable("CAPY_NX_CALIBRATION_OUT")
        If String.IsNullOrEmpty(root) Then Throw New ArgumentException("Set CAPY_NX_CALIBRATION_OUT.")
        Dim outDir = Path.Combine(root, "nx")
        Directory.CreateDirectory(outDir)
        Dim prt = Path.Combine(outDir, "calibration.prt")
        Dim stl = Path.Combine(outDir, "calibration.stl")
        Dim stp = Path.Combine(outDir, "calibration.step")
        For Each outputPath As String In {prt, stl, stp}
            If File.Exists(outputPath) Then Throw New IOException("Use a fresh output folder: " & outputPath)
        Next

        Dim nxSession As NXOpen.Session = NXOpen.Session.GetSession()
        Dim part = CType(nxSession.Parts.NewBaseDisplay(prt, BasePart.Units.Millimeters), Part)
        AddGauge(part, "XYZ_GAUGE_1000x200x300_MM", New Point3d(0, 0, 0), "1000", "200", "300")
        For Each row As String In File.ReadAllLines(Path.Combine(root, "joint_map.csv"))
            Dim cols = row.Split(","c)
            If cols(0) = "boom_pivot" OrElse cols(0) = "stick_pivot" OrElse cols(0) = "bucket_pivot" Then
                Dim point = New Point3d(Double.Parse(cols(2), CultureInfo.InvariantCulture),
                                         Double.Parse(cols(3), CultureInfo.InvariantCulture),
                                         Double.Parse(cols(4), CultureInfo.InvariantCulture))
                AddGauge(part, cols(0), point, "40", "27", "31")
            End If
        Next
        part.Save(BasePart.SaveComponents.False, BasePart.CloseAfterSave.False).Dispose()

        Dim mesh = nxSession.DexManager.CreateStlCreator()
        Try
            mesh.OutputFile = stl
            mesh.OutputType = STLCreator.OutputTypeEnum.Binary
            mesh.ChordalTol = 0.05
            mesh.AdjacencyTol = 0.05
            mesh.AutoNormalGen = True
            For Each body As Body In part.Bodies
                mesh.ExportSelectionBlock.Add(body)
            Next
            mesh.Commit()
        Finally
            mesh.Destroy()
        End Try

        Dim neutral = nxSession.DexManager.CreateStep214Creator()
        Try
            neutral.SettingsFile = Path.Combine(Environment.GetEnvironmentVariable("UGII_BASE_DIR"),
                                                "STEP214UG", "step214ug.def")
            neutral.InputFile = prt
            neutral.OutputFile = stp
            neutral.ExportFrom = Step214Creator.ExportFromOption.DisplayPart
            neutral.ObjectTypes.Solids = True
            neutral.FileSaveFlag = False
            neutral.Commit()
        Finally
            neutral.Destroy()
        End Try
        If Not File.Exists(stl) OrElse Not File.Exists(stp) Then Throw New IOException("Export missing.")
        Console.WriteLine("NX_CALIBRATION_DONE")
    End Sub
End Module
