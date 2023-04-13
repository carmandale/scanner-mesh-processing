//
//  ContentView.swift
//  GJ_ImageLoader
//
//  Created by Dale Carman on 4/7/23.
//

import SwiftUI
import Combine
import SceneKit

struct ContentView: View {
    @State private var directoryURL: URL?
    @ObservedObject private var imageLoader = ImageLoader()

    var body: some View {
        VStack {
            if directoryURL != nil {
                ImageGridView(imageLoader: imageLoader)
            } else {
                FolderPicker(directoryURL: $directoryURL)
            }
        }
        .onAppear {
            NotificationCenter.default.addObserver(forName: .directoryURLChanged, object: nil, queue: .main) { notification in
                guard let url = directoryURL else { return }
                print("Selected directory: \(url.path)")
                imageLoader.loadImages(from: url.path)
            }
        }
    }
}

struct ModelURL: Identifiable {
    let id = UUID()
    let url: URL
}


struct ImageGridView: View {
    @ObservedObject var imageLoader: ImageLoader
    @State private var showModelInfo: Bool = false
    @State private var selectedModelURL: ModelURL?
    @State private var isLoading: Bool = false
    private let columns = [
        GridItem(.adaptive(minimum: 200))
    ]

    var body: some View {
        ScrollView {
            LazyVGrid(columns: columns) {
                ForEach(imageLoader.images, id: \.self) { url in
                    if let nsImage = NSImage(contentsOf: url) {
                        let scanId = url.deletingPathExtension().lastPathComponent
                        Button(action: {
                            selectedModelURL = ModelURL(url: url.deletingLastPathComponent().appendingPathComponent("baked_mesh.usda"))
                            showModelInfo.toggle()
                        })  {
                            VStack {
                                Image(nsImage: nsImage)
                                    .resizable()
                                    .scaledToFit()
                                Text(scanId)
                                    .font(.headline)
                            }
                        }
                        .buttonStyle(PlainButtonStyle())
                    }
                }
            }
        }
        .padding()
        .navigationTitle("Images")
        .sheet(item: $selectedModelURL, onDismiss: { isLoading = false }) { modelURL in
            ZStack {
                if isLoading {
                    Color.black
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle())
                        .scaleEffect(2)
                } else {
                    ModelView(modelURL: modelURL.url, isLoading: $isLoading)
                        .frame(minWidth: 500, minHeight: 500)
                        .transition(.opacity)
                        .animation(.easeInOut(duration: 0.5))
                }
            }
            .frame(minWidth: 500, minHeight: 500)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Close") {
                        selectedModelURL = nil
                    }
                }
            }
        }



        
    }
}


struct ModelView: NSViewRepresentable {
    var modelURL: URL
    @Binding var isLoading: Bool
    @State private var modelLoaded = false

    func makeNSView(context: Context) -> SCNView {
        let sceneView = SCNView()
        let scene = SCNScene()
        sceneView.scene = scene
        sceneView.allowsCameraControl = true
        sceneView.autoenablesDefaultLighting = true

        return sceneView
    }

    func updateNSView(_ nsView: SCNView, context: Context) {
        if !modelLoaded {
            isLoading = true
            DispatchQueue.global(qos: .userInitiated).async {
                do {
                    let model = try SCNScene(url: modelURL, options: [.preserveOriginalTopology: true])
                    DispatchQueue.main.async {
                        nsView.scene?.rootNode.addChildNode(model.rootNode)
                        isLoading = false
                        modelLoaded = true
                    }
                } catch {
                    print("Error loading model: \(error)")
                    isLoading = false
                }
            }
        }
    }
}


extension Notification.Name {
    static let directoryURLChanged = Notification.Name("directoryURLChanged")
}



