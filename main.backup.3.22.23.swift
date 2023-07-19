/*
See LICENSE folder for this sample’s licensing information.

Abstract:
RealityKit Object Creation command line tools.
*/

import ArgumentParser  // Available from Apple: https://github.com/apple/swift-argument-parser
import Foundation
import os
import RealityKit
import Metal
import ModelIO
import CoreImage

let logger = Logger(subsystem: "com.groove-jones.groove-mesher",
                            category: "GrooveMesher")

/// Checks to make sure at least one GPU meets the minimum requirements for object reconstruction. At
/// least one GPU must be a "high power" device, which means it has at least 4 GB of RAM, provides
/// barycentric coordinates to the fragment shader, and is running on an Apple silicon Mac or an Intel Mac
/// with a discrete GPU.
private func supportsObjectReconstruction() -> Bool {
    for device in MTLCopyAllDevices() where
        !device.isLowPower &&
         device.areBarycentricCoordsSupported &&
         device.recommendedMaxWorkingSetSize >= UInt64(4e9) {
        return true
    }
    return false
}

/// Returns `true` if at least one GPU has hardware support for ray tracing. The GPU that supports ray
/// tracing need not be the same GPU that supports object reconstruction.
private func supportsRayTracing() -> Bool {
    for device in MTLCopyAllDevices() where device.supportsRaytracing {
        return true
    }
    return false
}

/// Returns `true` if the current hardware supports Object Capture.
func supportsObjectCapture() -> Bool {
    return supportsObjectReconstruction() && supportsRayTracing()
}

/// Implements the main command structure, defines the command-line arguments,
/// and specifies the main run loop.
struct GrooveMesher: ParsableCommand {
    
    private typealias Configuration = PhotogrammetrySession.Configuration
    private typealias Request = PhotogrammetrySession.Request
    
    public static let configuration = CommandConfiguration(
        abstract: "Reconstructs 3D USDZ model from a folder of images.")
    
    // group to synchronize our requests
    public static let group = DispatchGroup()
    
    @Argument(help: "The local input file folder of images.")
    private var inputFolder: String
    
    @Argument(help: "Full path to the USDZ output file.")
    private var outputFolder: String
    
    @Option(name: .shortAndLong,
            parsing: .next,
            help: "detail {preview, reduced, medium, full, raw}  Detail of output model in terms of mesh size and texture size .",
            transform: Request.Detail.init)
    private var detail: Request.Detail? = nil
    
    @Option(name: [.customShort("o"), .long],
            parsing: .next,
            help: "sampleOrdering {unordered, sequential}  Setting to sequential may speed up computation if images are captured in a spatially sequential pattern.",
            transform: Configuration.SampleOrdering.init)
    private var sampleOrdering: Configuration.SampleOrdering?
    
    @Option(name: .shortAndLong,
            parsing: .next,
            help: "featureSensitivity {normal, high}  Set to high if the scanned object does not contain a lot of discernible structures, edges or textures.",
            transform: Configuration.FeatureSensitivity.init)
    private var featureSensitivity: Configuration.FeatureSensitivity?
    
    @Option(name: [.customShort("x"), .customLong("minX")],
            parsing: .next,
            help: "customBoundingBox minimum x.")
    private var minimumX: Float?
    
    @Option(name: [.customLong("maxX")],
            parsing: .next,
            help: "customBoundingBox maximum x.")
    private var maximumX: Float?
    
    @Option(name: [.customShort("p"), .long],
            parsing: .next,
            help: "a custom value for the floor to be able to adjust the cutoff value")
    private var customFloorPad: Float?
    
    @Option(name: [.customShort("y"), .customLong("minY")],
            parsing: .next,
            help: "customBoundingBox minimum y.")
    private var minimumY: Float?
    
    @Option(name: [.customLong("maxY")],
            parsing: .next,
            help: "customBoundingBox maximum y.")
    private var maximumY: Float?
    
    @Option(name: [.customShort("z"), .customLong("minZ")],
            parsing: .next,
            help: "customBoundingBox minimum Z.")
    private var minimumZ: Float?
    
    @Option(name: [.customLong("maxZ")],
            parsing: .next,
            help: "customBoundingBox maximum Z.")
    private var maximumZ: Float?
    

    
    /// The main run loop entered at the end of the file.
    func run() {
        guard supportsObjectCapture() else {
            print("💩 Program terminated early because the hardware doesn't support Object Capture.")
            print("Object Capture is not available on this computer.")
            Foundation.exit(1)
        }
        
        // create photogrammetry samples
//        let samples = getSamplesFromFiles()
        let inputFolderUrl = URL(fileURLWithPath: inputFolder, isDirectory: true)
        extractDepthData(inputFolderUrl: inputFolderUrl)

        let configuration = makeConfigurationFromArguments()
        print("Using configuration: \(String(describing: configuration))")

        // Try to create the session, or else exit.
        var maybeSession: PhotogrammetrySession? = nil
        do {
            maybeSession = try PhotogrammetrySession(input: inputFolderUrl, configuration: configuration)
//            maybeSession = try PhotogrammetrySession(input: samples, configuration: configuration)
            print("Successfully created session.")
        } catch {
            fatalError("💩 Error creating session: \(String(describing: error))")
        }
        guard let session = maybeSession else {
            Foundation.exit(1)
        }
        
        let waiter = Task {
            do {
                for try await output in session.outputs {
                    switch output {
                        case .processingComplete:
                        print("Processing is complete!")
                        // process remaining requests or else exit
                        // Foundation.exit(0)
                        case .requestError(let request, let error):
                            print("💩 Request \(String(describing: request)) had an error: \(String(describing: error))")
                        case .requestComplete(let request, let result):
                            GrooveMesher.handleRequestComplete(request: request, result: result)
                        case .requestProgress(let request, let fractionComplete):
                            GrooveMesher.handleRequestProgress(request: request, fractionComplete: fractionComplete)
                        case .inputComplete:  // data ingestion only!
                            print("Data ingestion is complete.  Beginning processing...")
                        case .invalidSample(let id, let reason):
                            print("💩 Invalid Sample! id=\(id)  reason=\"\(reason)\"")
                        case .skippedSample(let id):
                            print("💩 Sample id=\(id) was skipped by processing.")
                        case .automaticDownsampling:
                            print("💩 Automatic downsampling was applied!")
                        case .processingCancelled:
                            print("💩 Processing was cancelled.")
                        @unknown default:
                            print("💩 Output: unhandled message: \(output.localizedDescription)")
                    }
                }
            } catch {
                fatalError("💩 Output: ERROR = \(String(describing: error))")
            }
        }
        
        // The compiler may deinitialize these objects since they may appear to be
        // unused. This keeps them from being deallocated until they exit.
        withExtendedLifetime((session, waiter)) {
            // Run the main process call on the request, then enter the main run
            // loop until you get the published completion event or error.
            do {
//                let requests: [PhotogrammetrySession.Request] = [makeRequestOfBounds(), makeRequestForPreview(), makeRequestFromArguments()]
//                print("Using requests: \(String(describing: requests))")
                
                GrooveMesher.group.enter()
                let previewRequest = makeRequestForPreview()
                try session.process(requests: [previewRequest])
                print("🟢 Started Preview Request \(String(describing: previewRequest))")

                /// Modify the GrooveMesher.group.notify to include finding the bounding box of the scanned person
                GrooveMesher.group.notify(queue: .main) {
                    // Find the bounding box of the scanned person
                    let personBoundingBox = findBoundingBoxOfScannedPerson(previewModelURL: previewModelURL)

                    let finalRequest = makeRequestFromArguments(customBoundingBox: personBoundingBox)
                    try! session.process(requests: [finalRequest])
                    print("🟢 Started Final Request \(String(describing: finalRequest))")
                }
                // Enter the infinite loop dispatcher used to process asynchronous
                // blocks on the main queue. You explicitly exit above to stop the loop.
                RunLoop.main.run()
            } catch {
                fatalError("Process got error: \(String(describing: error))")
            }
        }
    }

    /// Creates the session configuration by overriding any defaults with arguments specified.
    private func makeConfigurationFromArguments() -> PhotogrammetrySession.Configuration {
        var configuration = PhotogrammetrySession.Configuration()
        sampleOrdering.map { configuration.sampleOrdering = $0 }
        featureSensitivity.map { configuration.featureSensitivity = $0 }
        configuration.isObjectMaskingEnabled = false
        return configuration
    }

    /// Creates a request to use based on the command-line arguments.
    private func makeRequestFromArguments(customBoundingBox: BoundingBox) -> PhotogrammetrySession.Request {
//        let offsetX = (customBBoxOffsetX ?? 0.0) * (customBBoxOffsetSignX == "negative" ? -1.0 : 1.0)
//        let offsetZ = (customBBoxOffsetZ ?? 0.0) * (customBBoxOffsetSignZ == "negative" ? -1.0 : 1.0)
        let outputUrl = URL(fileURLWithPath: outputFolder)
//        let floorYCoordinate = extractFloorYCoordinate()
//        let customBoundingBox = BoundingBox(min: SIMD3<Float>((minimumX ?? -0.74), (minimumY ?? (floorYCoordinate + (customFloorPad ?? 0.03))), (minimumZ ?? -0.74)),
//                                                               max: SIMD3<Float>((maximumX ?? 0.74), (maximumY ?? 1.2), (maximumZ ?? 0.74)))
        let geometry = PhotogrammetrySession.Request.Geometry(bounds: customBoundingBox,
                                                                  transform: Transform(scale: SIMD3(x:1, y:1, z:1),
                                                                                       rotation: simd_quatf(angle: 2 * Float.pi, axis: SIMD3(x: 1, y: 0, z: 0)),
                                                                                       translation: SIMD3<Float>(0.0, 0.0, 0.0)))

            if let detailSetting = detail {
                let request = PhotogrammetrySession.Request.modelFile(url: outputUrl, detail: detailSetting, geometry: geometry)
                print("⭐️ Creating request from arguments \(String(describing: request))")
                return request
            } else {
                return PhotogrammetrySession.Request.modelFile(url: outputUrl)
            }
    }
    
    private func extractFloorYCoordinate() -> Float {
        let pathString = outputFolder + "preview.usdz"
        guard FileManager.default.fileExists(atPath: pathString) else {
            fatalError("💩 Can't find a preview file at \(pathString)")
        }
        let url = URL(fileURLWithPath: pathString)
        let asset = MDLAsset(url: url)
        print("📦 preview object's bounding box: \(asset.boundingBox)")
        return asset.boundingBox.minBounds.y
    }
    
    /// Create a function to find the bounding box of the scanned person
    func findBoundingBoxOfScannedPerson(previewModelURL: URL) -> BoundingBox {
        // Your logic to calculate the bounding box of the scanned person in the middle
        // ...
        return calculatedBoundingBox
    }

    
    /// Creates a request for a preview.
    private func makeRequestForPreview() -> PhotogrammetrySession.Request {
        let outputUrl = URL(fileURLWithPath: outputFolder + "preview.usdz")
        let request = PhotogrammetrySession.Request.modelFile(url: outputUrl, detail: .preview)
        print("⭐️ Creating request for preview \(String(describing: request))")
        return request
    }
    
    /// Gets bounds of request
    private func makeRequestOfBounds() -> PhotogrammetrySession.Request {
        return PhotogrammetrySession.Request.bounds
    }
    
    /// Called when the the session sends a request completed message.
    private static func handleRequestComplete(request: PhotogrammetrySession.Request,
                                              result: PhotogrammetrySession.Result) {
        print("Request complete: \(String(describing: request)) with result...")
        switch result {
        case .modelFile(let url):
            print("\t ✅ modelFile available at url=\(url)")
            if url.deletingPathExtension().lastPathComponent == "preview" {
                GrooveMesher.group.leave()
            } else {
                Foundation.exit(0)
            }
        case .bounds(let boundingBox):
            print("\t 📦 These are your bounds: \(String(describing: boundingBox))")
        default:
            print("❓ \tUnexpected result: \(String(describing: result))")
        }
    }
    
    /// Called when the sessions sends a progress update message.
    private static func handleRequestProgress(request: PhotogrammetrySession.Request, fractionComplete: Double) {
        let percentage = Int(fractionComplete * 100)
        print("Progress = \(percentage)%")
    }

}

// MARK: - Helper Functions / Extensions

private func handleRequestProgress(request: PhotogrammetrySession.Request, fractionComplete: Double) {
    print("Progress(request = \(String(describing: request)) = \(fractionComplete)")
}

/// Error thrown when an illegal option is specified.
private enum IllegalOption: Swift.Error {
    case invalidDetail(String)
    case invalidSampleOverlap(String)
    case invalidSampleOrdering(String)
    case invalidFeatureSensitivity(String)
}

/// Extension to add a throwing initializer used as an option transform to verify the user-supplied arguments.
@available(macOS 12.0, *)
extension PhotogrammetrySession.Request.Detail {
    init(_ detail: String) throws {
        switch detail {
            case "preview": self = .preview
            case "reduced": self = .reduced
            case "medium": self = .medium
            case "full": self = .full
            case "raw": self = .raw
            default: throw IllegalOption.invalidDetail(detail)
        }
    }
}

@available(macOS 12.0, *)
extension PhotogrammetrySession.Configuration.SampleOrdering {
    init(sampleOrdering: String) throws {
        if sampleOrdering == "unordered" {
            self = .unordered
        } else if sampleOrdering == "sequential" {
            self = .sequential
        } else {
            throw IllegalOption.invalidSampleOrdering(sampleOrdering)
        }
    }
}

@available(macOS 12.0, *)
extension PhotogrammetrySession.Configuration.FeatureSensitivity {
    init(featureSensitivity: String) throws {
        if featureSensitivity == "normal" {
            self = .normal
        } else if featureSensitivity == "high" {
            self = .high
        } else {
            throw IllegalOption.invalidFeatureSensitivity(featureSensitivity)
        }
    }
}

// MARK: - Main

// Run the program until completion.
if #available(macOS 12.0, *) {
    GrooveMesher.main()
} else {
    fatalError("Requires minimum macOS 12.0!")
}

extension GrooveMesher {
    func extractDepthData(inputFolderUrl: URL) {
        print("extracting depth data...")
        // extracting urls
        var urls: [URL] = []
        
        // load urls to the memory
        do {
            let allUrls = try FileManager.default.contentsOfDirectory(at: inputFolderUrl, includingPropertiesForKeys: nil, options: [])
            urls = allUrls.filter{ extractType(from: $0) == .image }
        } catch {
            fatalError("💩 \(error.localizedDescription)")
        }
        
        urls.forEach {
            guard let depthDataMapRay = depthDataMap(forItemAt: $0) else { fatalError() }
            depthDataMapRay.normalize()
            
            let filename = $0.deletingPathExtension().lastPathComponent
            let depthMapRayUrl = inputFolderUrl.appendingPathComponent("\(filename).tif", isDirectory: false)
            
            let depthImage = CIImage( cvImageBuffer: depthDataMapRay,
                                      options: [ .auxiliaryDisparity: true ] )
            if let colorSpace = CGColorSpace(name: CGColorSpace.linearGray),
               let depthMapRayData = CIContext().tiffRepresentation(of: depthImage,
                                                      format: .Lf,
                                                      colorSpace: colorSpace,
                                                                    options: [.disparityImage: depthImage]) {
            
//                print("Writing depth data Ray to path=\"\(depthMapRayUrl.path)\"...")
                do {
                    try depthMapRayData.write(to: URL(fileURLWithPath: depthMapRayUrl.path), options: .atomic)
                } catch {
                    print("💩 Can't write depth Ray tiff to: \"\(depthMapRayUrl.path)\" error=\(String(describing: error))")
                }
            } else {
                fatalError()
            }
        }
    }
    
    private func getSamplesFromFiles() -> [PhotogrammetrySample] {
        // extracting urls
        let folderUrl = URL(fileURLWithPath: inputFolder)
        var urls: [URL] = []
        
        // load file urls to the memory
        do {
            urls = try FileManager.default.contentsOfDirectory(at: folderUrl, includingPropertiesForKeys: nil, options: [])
        } catch {
            fatalError("💩 \(error.localizedDescription)")
        }

        // extract id and types from filenames
        var allFiles: [File] = []
        urls.forEach { url in
            let type = extractType(from: url)
            let id = extractId(from: url)
            allFiles.append(File(id: id, type: type, url: url))
        }
        print("\(allFiles.count) files were found. Creating samples from them...")
        
        // create samples
        let allSamples = allFiles.reduce(into: [Sample]()) { partialResult, file in
            if let sampleIdx = partialResult.firstIndex(where: { $0.id == file.id }) {
                partialResult[sampleIdx].addValue(file: file)
            } else {
                var newSample = Sample(id: file.id)
                newSample.addValue(file: file)
                partialResult.append(newSample)
            }
        }
    
        // count samples
        let imageCount = allSamples.filter { $0.image != nil }.count
        let depthMapCount = allSamples.filter { $0.depthDataMap != nil }.count
        let gravityCount = allSamples.filter { $0.gravityVector != nil }.count
        let segmentationMasksCount = allSamples.filter { $0.objectMask != nil }.count
        let metadataCount = allSamples.filter { $0.metadata.count > 0 }.count
        print("➡️ \(allSamples.count) samples were created: \(imageCount) images, \(depthMapCount) depth maps, \(gravityCount) gravity vectors, \(segmentationMasksCount) object masks, \(metadataCount) metadatas.")
        return allSamples.map { PhotogrammetrySample(from: $0) }
    }
}
