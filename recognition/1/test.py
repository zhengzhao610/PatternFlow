# Setup the optimizer and loss function
smooth=1
def dice_coef(trainGen,testGen, smooth=1):
  intersection = K.sum(trainGen* testGen, axis=[1,2,3])
  union = K.sum(trainGen, axis=[1,2,3]) + K.sum(testGen, axis=[1,2,3])
  dice = K.mean((2. * intersection + smooth)/(union + smooth), axis=0)
  return dice

def dice_coef_loss(trainGen,testGen):
  return -dice_coef(trainGen, testGen)

model.compile(optimizer=Adam(lr=1e-4), loss=-dice_coef_loss, metrics=[dice_coef])

# Set the proper checkpoint callback to save model.
model_checkpoint = ModelCheckpoint(
    'best_model.hdf5', monitor='loss', verbose=1, save_best_only=True)

# Model training.
history = model.fit_generator(
    trainGen,
    steps_per_epoch=train_steps,
    epochs=epochs,
    callbacks=[model_checkpoint],
    validation_data=valGen,
    validation_steps=validate_steps,
)

# Load the best model.
model = load_model('best_model.hdf5', compile=True)

# Model
example_image = "./data/keras_png_slices_test/case_441_slice_0.nii.png"
example_label = "./data/keras_png_slices_seg_test/seg_441_slice_0.nii.png"

# Read the images.
img = io.imread(example_image, as_gray=True)
img = img / 255.0
img = np.reshape(img, (1,) + img.shape)

# Get the predictions.
prob_predictions = model.predict(img)
final_predicitons = np.argmax(prob_predictions, axis=-1)

# Convert the one-hot predictions to image colors.
predictions = np.zeros(final_predicitons.shape, dtype=np.float32)
predictions[final_predicitons == 1] = 85.0
predictions[final_predicitons == 2] = 170.0
predictions[final_predicitons == 3] = 255.0

# Plot the image/prediction/groundtruth.
plt.subplot(131)
plt.imshow(img[0])
plt.title('Image')
plt.subplot(132)
plt.imshow(predictions[0])
plt.title('Prediction')
plt.subplot(133)
label = io.imread(example_label, as_gray=True)
plt.imshow(label)
plt.title('Groundtruth')
plt.show()