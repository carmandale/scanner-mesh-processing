//
//  ImageLoader.swift
//  GJ_ImageLoader
//
//  Created by Dale Carman on 4/7/23.
//

import Foundation
import Combine
import SwiftUI

class ImageLoader: ObservableObject {
    @Published var images: [URL] = []
    private var path: String?
    private var fileManager: FileManager
    private var cancellables: Set<AnyCancellable> = []
    
    init() {
        self.fileManager = FileManager.default
        print("ImageLoader - init")
    }
    
    func loadImages(from path: String) {
        self.path = path
        loadImageURLs()
        DispatchQueue.main.async {
            self.objectWillChange.send()
        }
        print("ImageLoader - loadImages - path: \(path)")
        print("ImageLoader - loadImages - images: \(images)")
    }

    
    private func loadImageURLs() {
        guard let path = self.path else { return }
        let url = URL(fileURLWithPath: path)

        do {
            var imageUrls: [URL] = []
            let subdirectoryUrls = try fileManager.contentsOfDirectory(at: url, includingPropertiesForKeys: nil, options: [.skipsHiddenFiles])
            for subdirectoryUrl in subdirectoryUrls {
                let subdirectoryName = subdirectoryUrl.lastPathComponent
                let pngUrl = subdirectoryUrl.appendingPathComponent("photogrammetry").appendingPathComponent("\(subdirectoryName).png")
                if fileManager.fileExists(atPath: pngUrl.path) {
                    imageUrls.append(pngUrl)
                }
            }
            self.images = imageUrls
            
            print("Loading images from path: \(path)")
            print("Image URLs found: \(imageUrls)")
        } catch {
            print("Error loading images: \(error)")
        }
    }



}
