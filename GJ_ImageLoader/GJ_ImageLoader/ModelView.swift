//
//  ModelView.swift
//  GJ_ImageLoader
//
//  Created by Dale Carman on 4/7/23.
//
//
//import SwiftUI
//import SceneKit
//
//struct ModelView: UIViewRepresentable {
//    var modelURL: URL
//
//    func makeUIView(context: Context) -> SCNView {
//        let sceneView = SCNView()
//        return sceneView
//    }
//
//    func updateUIView(_ uiView: SCNView, context: Context) {
//        let scene = SCNScene()
//        uiView.scene = scene
//        uiView.allowsCameraControl = true
//        uiView.autoenablesDefaultLighting = true
//
//        do {
//            let model = try SCNScene(url: modelURL, options: [.sceneSourceLoadingOptionPreserveOriginalTopology: true])
//            scene.rootNode.addChildNode(model.rootNode)
//        } catch {
//            print("Error loading model: \(error)")
//        }
//    }
//}
